'use client';

import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import * as THREE from 'three';

// ── Recent actions data (will come from API later) ──
const RECENT_ACTIONS = [
    { id: 1, city: 'Hyderabad', lat: 17.3850, lon: 78.4867, type: 'solar_panels', co2: 2.5, conf: 99.95 },
    { id: 2, city: 'Karachi', lat: 24.8607, lon: 67.0011, type: 'cycling', co2: 0.8, conf: 97.2 },
    { id: 3, city: 'Lahore', lat: 31.5497, lon: 74.3436, type: 'solar_panels', co2: 2.5, conf: 98.1 },
    { id: 4, city: 'Mumbai', lat: 19.0760, lon: 72.8777, type: 'cycling', co2: 0.8, conf: 96.4 },
    { id: 5, city: 'Delhi', lat: 28.6139, lon: 77.2090, type: 'utility_bills', co2: 1.2, conf: 94.8 },
];

function latLonToVector3(lat: number, lon: number, radius: number) {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lon + 180) * (Math.PI / 180);
    return new THREE.Vector3(
        -radius * Math.sin(phi) * Math.cos(theta),
        radius * Math.cos(phi),
        radius * Math.sin(phi) * Math.sin(theta)
    );
}

export default function EcoXGlobe() {
    const mountRef = useRef<HTMLDivElement>(null);
    const sceneRef = useRef<THREE.Scene | null>(null);
    const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
    const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
    const globeRef = useRef<THREE.Mesh | null>(null);
    const frameRef = useRef<number>(0);
    const lasersRef = useRef<THREE.Line[]>([]);

    const [activeAction, setActiveAction] = useState(RECENT_ACTIONS[0]);
    const [stats, setStats] = useState({ totalCO2: 0, totalActions: 0, topCity: 'Hyderabad' });
    const [actionIndex, setActionIndex] = useState(0);

    // ── Three.js globe ──
    useEffect(() => {
        if (!mountRef.current) return;

        const W = mountRef.current.clientWidth;
        const H = mountRef.current.clientHeight;

        // Scene
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x020d18);
        sceneRef.current = scene;

        // Stars
        const starGeo = new THREE.BufferGeometry();
        const stars = new Float32Array(6000);
        for (let i = 0; i < 6000; i++) stars[i] = (Math.random() - 0.5) * 800;
        starGeo.setAttribute('position', new THREE.BufferAttribute(stars, 3));
        scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.4 })));

        // Camera
        const camera = new THREE.PerspectiveCamera(45, W / H, 0.1, 1000);
        camera.position.set(0, 0, 3.5);
        cameraRef.current = camera;

        // Renderer
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(W, H);
        renderer.setPixelRatio(window.devicePixelRatio);
        mountRef.current.appendChild(renderer.domElement);
        rendererRef.current = renderer;

        // Globe
        const geo = new THREE.SphereGeometry(1, 64, 64);
        const mat = new THREE.MeshPhongMaterial({
            color: 0x0a3d6b,
            emissive: 0x0a1f3a,
            shininess: 80,
            wireframe: false,
        });
        const globe = new THREE.Mesh(geo, mat);
        scene.add(globe);
        globeRef.current = globe;

        // Wireframe overlay
        const wireMat = new THREE.MeshBasicMaterial({ color: 0x00ff88, wireframe: true, opacity: 0.06, transparent: true });
        scene.add(new THREE.Mesh(geo, wireMat));

        // Atmosphere glow
        const atmGeo = new THREE.SphereGeometry(1.08, 64, 64);
        const atmMat = new THREE.MeshBasicMaterial({ color: 0x00aaff, transparent: true, opacity: 0.06, side: THREE.BackSide });
        scene.add(new THREE.Mesh(atmGeo, atmMat));

        // Lights
        scene.add(new THREE.AmbientLight(0x223344, 2));
        const sun = new THREE.DirectionalLight(0x4488ff, 3);
        sun.position.set(5, 3, 5);
        scene.add(sun);

        // Animate
        const animate = () => {
            frameRef.current = requestAnimationFrame(animate);
            globe.rotation.y += 0.0015;

            // Fade lasers
            lasersRef.current.forEach(l => {
                const mat = l.material as THREE.LineBasicMaterial;
                if (mat.opacity > 0) mat.opacity -= 0.008;
            });

            renderer.render(scene, camera);
        };
        animate();

        // Resize
        const onResize = () => {
            if (!mountRef.current) return;
            const w = mountRef.current.clientWidth;
            const h = mountRef.current.clientHeight;
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
            renderer.setSize(w, h);
        };
        window.addEventListener('resize', onResize);

        return () => {
            window.removeEventListener('resize', onResize);
            cancelAnimationFrame(frameRef.current);
            renderer.dispose();
            mountRef.current?.removeChild(renderer.domElement);
        };
    }, []);

    // ── Fire laser on action change ──
    useEffect(() => {
        if (!sceneRef.current || !globeRef.current) return;

        const action = RECENT_ACTIONS[actionIndex];
        setActiveAction(action);

        // Create laser from surface outward
        const origin = latLonToVector3(action.lat, action.lon, 1.0);
        const tip = latLonToVector3(action.lat, action.lon, 1.6);

        const pts = [origin, tip];
        const geo = new THREE.BufferGeometry().setFromPoints(pts);
        const mat = new THREE.LineBasicMaterial({ color: 0x00ff88, transparent: true, opacity: 1.0, linewidth: 2 });
        const laser = new THREE.Line(geo, mat);
        sceneRef.current.add(laser);
        lasersRef.current.push(laser);

        // Dot on surface
        const dotGeo = new THREE.SphereGeometry(0.025, 8, 8);
        const dotMat = new THREE.MeshBasicMaterial({ color: 0x00ff88 });
        const dot = new THREE.Mesh(dotGeo, dotMat);
        dot.position.copy(origin);
        sceneRef.current.add(dot);

        // Update stats
        setStats(prev => ({
            totalCO2: parseFloat((prev.totalCO2 + action.co2).toFixed(2)),
            totalActions: prev.totalActions + 1,
            topCity: action.city,
        }));

        // Cleanup old lasers
        if (lasersRef.current.length > 20) {
            const old = lasersRef.current.shift();
            if (old) sceneRef.current.remove(old);
        }
    }, [actionIndex]);

    // ── Auto-cycle actions ──
    useEffect(() => {
        const timer = setInterval(() => {
            setActionIndex(i => (i + 1) % RECENT_ACTIONS.length);
        }, 3000);
        return () => clearInterval(timer);
    }, []);

    const typeIcon: Record<string, string> = {
        solar_panels: '☀️',
        cycling: '🚴',
        utility_bills: '⚡',
    };

    return (
        <div className="relative w-full h-screen bg-[#020d18] overflow-hidden font-mono">

            {/* Globe canvas */}
            <div ref={mountRef} className="absolute inset-0" />

            {/* Top bar */}
            <motion.div
                initial={{ opacity: 0, y: -30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 1 }}
                className="absolute top-0 left-0 right-0 flex items-center justify-between px-8 py-5 z-10"
            >
                <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full bg-[#00ff88] animate-pulse" />
                    <span className="text-[#00ff88] text-xl font-bold tracking-widest">ECO X</span>
                    <span className="text-[#00ff88]/40 text-xs tracking-widest">PROOF OF PLANET</span>
                </div>
                <div className="flex gap-6 text-xs text-[#00ff88]/60 tracking-widest">
                    <span>POLYGON AMOY</span>
                    <span>•</span>
                    <span>NASA POWER API</span>
                    <span>•</span>
                    <span>IPCC AR6</span>
                </div>
            </motion.div>

            {/* Left stats panel */}
            <motion.div
                initial={{ opacity: 0, x: -40 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 1, delay: 0.3 }}
                className="absolute left-8 top-1/2 -translate-y-1/2 z-10 flex flex-col gap-4"
            >
                {[
                    { label: 'CO₂ SAVED', value: `${stats.totalCO2} kg`, color: '#00ff88' },
                    { label: 'ACTIONS', value: stats.totalActions.toString(), color: '#00ccff' },
                    { label: 'TOP CITY', value: stats.topCity, color: '#ffaa00' },
                ].map((s) => (
                    <motion.div
                        key={s.label}
                        whileHover={{ scale: 1.05 }}
                        className="border border-[#00ff88]/20 bg-[#020d18]/80 backdrop-blur px-5 py-3 rounded"
                    >
                        <div className="text-[10px] tracking-widest" style={{ color: s.color + '80' }}>{s.label}</div>
                        <motion.div
                            key={s.value}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-lg font-bold"
                            style={{ color: s.color }}
                        >
                            {s.value}
                        </motion.div>
                    </motion.div>
                ))}
            </motion.div>

            {/* Right — active action card */}
            <motion.div
                initial={{ opacity: 0, x: 40 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 1, delay: 0.5 }}
                className="absolute right-8 top-1/2 -translate-y-1/2 z-10 w-64"
            >
                <AnimatePresence mode="wait">
                    <motion.div
                        key={activeAction.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.4 }}
                        className="border border-[#00ff88]/30 bg-[#020d18]/90 backdrop-blur rounded p-5"
                    >
                        <div className="text-[10px] text-[#00ff88]/50 tracking-widest mb-3">LIVE ACTION</div>
                        <div className="text-3xl mb-2">{typeIcon[activeAction.type] || '🌱'}</div>
                        <div className="text-[#00ff88] font-bold text-lg">{activeAction.city}</div>
                        <div className="text-[#00ff88]/60 text-xs mt-1 tracking-widest">
                            {activeAction.type.replace('_', ' ').toUpperCase()}
                        </div>
                        <div className="mt-4 pt-4 border-t border-[#00ff88]/10 grid grid-cols-2 gap-3">
                            <div>
                                <div className="text-[9px] text-[#00ff88]/40 tracking-widest">CO₂ SAVED</div>
                                <div className="text-[#00ff88] font-bold">{activeAction.co2} kg</div>
                            </div>
                            <div>
                                <div className="text-[9px] text-[#00ff88]/40 tracking-widest">AI CONFIDENCE</div>
                                <div className="text-[#00ccff] font-bold">{activeAction.conf}%</div>
                            </div>
                        </div>
                        <div className="mt-3 text-[9px] text-[#00ff88]/30 tracking-widest">
                            ✨ ARCTIC COOLED: 2,026,218 mm²
                        </div>
                    </motion.div>
                </AnimatePresence>
            </motion.div>

            {/* Bottom — QuantumLock 2050 */}
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 1, delay: 0.7 }}
                className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 text-center"
            >
                <div className="border border-[#ffaa00]/30 bg-[#020d18]/80 backdrop-blur px-8 py-3 rounded-full inline-flex items-center gap-4">
                    <div className="w-2 h-2 rounded-full bg-[#ffaa00] animate-pulse" />
                    <span className="text-[#ffaa00]/80 text-xs tracking-widest">QUANTUM-LOCK 2050</span>
                    <span className="text-[#ffaa00] font-bold text-sm">0.025 ECOX LOCKED</span>
                    <div className="w-2 h-2 rounded-full bg-[#ffaa00] animate-pulse" />
                </div>
            </motion.div>

        </div>
    );
}