'use client';

import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import * as THREE from 'three';

interface Action {
    id: number; city: string; country: string; lat: number; lon: number;
    type: string; co2: number; conf: number;
}

const ACTIONS: Action[] = [
    { id: 1, city: 'Karachi', country: 'Pakistan', lat: 24.86, lon: 67.00, type: 'cycling', co2: 0.8, conf: 97.2 },
    { id: 2, city: 'Lahore', country: 'Pakistan', lat: 31.55, lon: 74.34, type: 'solar_panels', co2: 2.5, conf: 98.1 },
    { id: 3, city: 'Islamabad', country: 'Pakistan', lat: 33.72, lon: 73.06, type: 'plantation', co2: 5.0, conf: 99.1 },
    { id: 4, city: 'Hyderabad', country: 'India', lat: 17.38, lon: 78.49, type: 'solar_panels', co2: 2.5, conf: 99.95 },
    { id: 5, city: 'Mumbai', country: 'India', lat: 19.08, lon: 72.88, type: 'cycling', co2: 0.8, conf: 96.4 },
    { id: 6, city: 'Delhi', country: 'India', lat: 28.61, lon: 77.21, type: 'utility_bills', co2: 1.2, conf: 94.8 },
    { id: 7, city: 'Bangalore', country: 'India', lat: 12.97, lon: 77.59, type: 'solar_panels', co2: 2.5, conf: 97.3 },
    { id: 8, city: 'London', country: 'UK', lat: 51.51, lon: -0.13, type: 'cycling', co2: 0.8, conf: 95.6 },
    { id: 9, city: 'Berlin', country: 'Germany', lat: 52.52, lon: 13.40, type: 'wind_energy', co2: 3.2, conf: 98.0 },
    { id: 10, city: 'Paris', country: 'France', lat: 48.86, lon: 2.35, type: 'cycling', co2: 0.8, conf: 96.1 },
    { id: 11, city: 'Amsterdam', country: 'Netherlands', lat: 52.37, lon: 4.90, type: 'cycling', co2: 0.8, conf: 99.2 },
    { id: 12, city: 'New York', country: 'USA', lat: 40.71, lon: -74.01, type: 'solar_panels', co2: 2.5, conf: 95.8 },
    { id: 13, city: 'Los Angeles', country: 'USA', lat: 34.05, lon: -118.24, type: 'solar_panels', co2: 2.5, conf: 97.1 },
    { id: 14, city: 'Toronto', country: 'Canada', lat: 43.65, lon: -79.38, type: 'wind_energy', co2: 3.2, conf: 96.5 },
    { id: 15, city: 'São Paulo', country: 'Brazil', lat: -23.55, lon: -46.63, type: 'plantation', co2: 5.0, conf: 98.3 },
    { id: 16, city: 'Buenos Aires', country: 'Argentina', lat: -34.60, lon: -58.38, type: 'solar_panels', co2: 2.5, conf: 94.9 },
    { id: 17, city: 'Cairo', country: 'Egypt', lat: 30.04, lon: 31.24, type: 'solar_panels', co2: 2.5, conf: 96.7 },
    { id: 18, city: 'Lagos', country: 'Nigeria', lat: 6.52, lon: 3.38, type: 'solar_panels', co2: 2.5, conf: 95.4 },
    { id: 19, city: 'Nairobi', country: 'Kenya', lat: -1.29, lon: 36.82, type: 'plantation', co2: 5.0, conf: 97.8 },
    { id: 20, city: 'Johannesburg', country: 'South Africa', lat: -26.20, lon: 28.04, type: 'solar_panels', co2: 2.5, conf: 96.2 },
    { id: 21, city: 'Dubai', country: 'UAE', lat: 25.20, lon: 55.27, type: 'solar_panels', co2: 2.5, conf: 98.5 },
    { id: 22, city: 'Riyadh', country: 'Saudi Arabia', lat: 24.69, lon: 46.72, type: 'solar_panels', co2: 2.5, conf: 97.4 },
    { id: 23, city: 'Tehran', country: 'Iran', lat: 35.69, lon: 51.39, type: 'utility_bills', co2: 1.2, conf: 94.1 },
    { id: 24, city: 'Istanbul', country: 'Turkey', lat: 41.01, lon: 28.95, type: 'cycling', co2: 0.8, conf: 96.8 },
    { id: 25, city: 'Moscow', country: 'Russia', lat: 55.75, lon: 37.62, type: 'wind_energy', co2: 3.2, conf: 95.3 },
    { id: 26, city: 'Beijing', country: 'China', lat: 39.91, lon: 116.39, type: 'solar_panels', co2: 2.5, conf: 97.6 },
    { id: 27, city: 'Shanghai', country: 'China', lat: 31.23, lon: 121.47, type: 'solar_panels', co2: 2.5, conf: 98.2 },
    { id: 28, city: 'Tokyo', country: 'Japan', lat: 35.68, lon: 139.69, type: 'solar_panels', co2: 2.5, conf: 99.0 },
    { id: 29, city: 'Seoul', country: 'South Korea', lat: 37.57, lon: 126.98, type: 'solar_panels', co2: 2.5, conf: 97.9 },
    { id: 30, city: 'Singapore', country: 'Singapore', lat: 1.35, lon: 103.82, type: 'solar_panels', co2: 2.5, conf: 98.7 },
    { id: 31, city: 'Bangkok', country: 'Thailand', lat: 13.75, lon: 100.52, type: 'cycling', co2: 0.8, conf: 95.1 },
    { id: 32, city: 'Jakarta', country: 'Indonesia', lat: -6.21, lon: 106.85, type: 'plantation', co2: 5.0, conf: 96.9 },
    { id: 33, city: 'Manila', country: 'Philippines', lat: 14.60, lon: 120.98, type: 'solar_panels', co2: 2.5, conf: 95.7 },
    { id: 34, city: 'Sydney', country: 'Australia', lat: -33.87, lon: 151.21, type: 'solar_panels', co2: 2.5, conf: 98.4 },
    { id: 35, city: 'Melbourne', country: 'Australia', lat: -37.81, lon: 144.96, type: 'wind_energy', co2: 3.2, conf: 97.5 },
    { id: 36, city: 'Auckland', country: 'New Zealand', lat: -36.85, lon: 174.76, type: 'wind_energy', co2: 3.2, conf: 98.1 },
    { id: 37, city: 'Dhaka', country: 'Bangladesh', lat: 23.81, lon: 90.41, type: 'solar_panels', co2: 2.5, conf: 94.6 },
    { id: 38, city: 'Colombo', country: 'Sri Lanka', lat: 6.93, lon: 79.85, type: 'solar_panels', co2: 2.5, conf: 96.3 },
    { id: 39, city: 'Kathmandu', country: 'Nepal', lat: 27.70, lon: 85.32, type: 'plantation', co2: 5.0, conf: 97.2 },
    { id: 40, city: 'Kabul', country: 'Afghanistan', lat: 34.53, lon: 69.17, type: 'solar_panels', co2: 2.5, conf: 93.8 },
    { id: 41, city: 'Madrid', country: 'Spain', lat: 40.42, lon: -3.70, type: 'solar_panels', co2: 2.5, conf: 97.0 },
    { id: 42, city: 'Rome', country: 'Italy', lat: 41.90, lon: 12.50, type: 'cycling', co2: 0.8, conf: 95.9 },
    { id: 43, city: 'Vienna', country: 'Austria', lat: 48.21, lon: 16.37, type: 'cycling', co2: 0.8, conf: 97.4 },
    { id: 44, city: 'Stockholm', country: 'Sweden', lat: 59.33, lon: 18.07, type: 'wind_energy', co2: 3.2, conf: 99.1 },
    { id: 45, city: 'Oslo', country: 'Norway', lat: 59.91, lon: 10.75, type: 'wind_energy', co2: 3.2, conf: 98.8 },
    { id: 46, city: 'Chicago', country: 'USA', lat: 41.88, lon: -87.63, type: 'wind_energy', co2: 3.2, conf: 96.0 },
    { id: 47, city: 'Mexico City', country: 'Mexico', lat: 19.43, lon: -99.13, type: 'solar_panels', co2: 2.5, conf: 95.5 },
    { id: 48, city: 'Lima', country: 'Peru', lat: -12.05, lon: -77.04, type: 'solar_panels', co2: 2.5, conf: 94.7 },
    { id: 49, city: 'Casablanca', country: 'Morocco', lat: 33.59, lon: -7.62, type: 'solar_panels', co2: 2.5, conf: 96.6 },
    { id: 50, city: 'Accra', country: 'Ghana', lat: 5.56, lon: -0.20, type: 'solar_panels', co2: 2.5, conf: 95.8 },
];

const ICONS: Record<string, string> = {
    solar_panels: '☀️', cycling: '🚴', utility_bills: '⚡', plantation: '🌱', wind_energy: '💨',
};

const MAX_LASERS = 50;
const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;
const FRAME_MS = isMobile ? 1000 / 30 : 1000 / 60;

// ── FIX: API_BASE — never a string literal ────────────────────────────────────
function getApiBase(): string {
    if (typeof window === 'undefined') return 'http://127.0.0.1:8000';
    const h = window.location.hostname;
    if (h === 'localhost' || h === '127.0.0.1') return 'http://127.0.0.1:8000';
    // Production: use env or derive from hostname
    if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, '');
    return `https://${h.replace('vercel.app', 'up.railway.app')}`;
}
const API_BASE = getApiBase();

async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/api/stats`, { mode: 'cors' });
        if (!res.ok) return null;
        return await res.json();
    } catch { return null; }
}

async function fetchRecentActions() {
    try {
        const res = await fetch(`${API_BASE}/api/recent-actions`, { mode: 'cors' });
        if (!res.ok) return null;
        return await res.json();
    } catch { return null; }
}

async function fetchGlobeData() {
    try {
        const res = await fetch(`${API_BASE}/api/globe-data`, { mode: 'cors' });
        if (!res.ok) return null;
        return await res.json();
    } catch { return null; }
}

const ATM_VERT = `
  varying vec3 vNormal;
  void main() {
    vNormal = normalize(normalMatrix * normal);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0);
  }
`;
const ATM_FRAG = `
  varying vec3 vNormal;
  void main() {
    float i = pow(0.65 - dot(vNormal, vec3(0,0,1)), 3.0);
    gl_FragColor = vec4(0.0, 0.9, 1.0, 1.0) * i;
  }
`;

// ── FIX 1: toVec3 — NaN guard ─────────────────────────────────────────────────
// Agar lat/lon NaN ya undefined ho toh THREE crash karta tha
// Ab safe defaults use karte hain (Karachi: 24.86, 67.00)
function toVec3(lat: number, lon: number, r: number): THREE.Vector3 {
    const safeLat = (typeof lat === 'number' && isFinite(lat)) ? lat : 24.86;
    const safeLon = (typeof lon === 'number' && isFinite(lon)) ? lon : 67.00;
    const phi = (90 - safeLat) * (Math.PI / 180);
    const theta = (safeLon + 180) * (Math.PI / 180);
    return new THREE.Vector3(
        -r * Math.sin(phi) * Math.cos(theta),
        r * Math.cos(phi),
        r * Math.sin(phi) * Math.sin(theta)
    );
}

class LaserPool {
    mesh: THREE.InstancedMesh;
    ages: Float32Array;
    count = 0;

    constructor(scene: THREE.Scene) {
        const geo = new THREE.CylinderGeometry(0.004, 0.004, 1, 4);
        const mat = new THREE.MeshBasicMaterial({ color: 0x00ff88, transparent: true, opacity: 1.0 });
        this.mesh = new THREE.InstancedMesh(geo, mat, MAX_LASERS);
        this.mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
        this.mesh.frustumCulled = false;
        this.ages = new Float32Array(MAX_LASERS).fill(0);
        const dummy = new THREE.Object3D();
        dummy.scale.set(0.001, 0.001, 0.001);
        dummy.updateMatrix();
        for (let i = 0; i < MAX_LASERS; i++) this.mesh.setMatrixAt(i, dummy.matrix);
        this.mesh.instanceMatrix.needsUpdate = true;
        scene.add(this.mesh);
    }

    // ── FIX 2: add() — NaN check before setFromUnitVectors ───────────────────
    // setFromUnitVectors crashes if dir is zero vector (when origin === tip)
    add(lat: number, lon: number) {
        // Sanitize inputs
        const safeLat = (typeof lat === 'number' && isFinite(lat)) ? lat : 24.86;
        const safeLon = (typeof lon === 'number' && isFinite(lon)) ? lon : 67.00;

        const i = this.count % MAX_LASERS;
        const origin = toVec3(safeLat, safeLon, 1.02);
        const tip = toVec3(safeLat, safeLon, 1.7);
        const mid = origin.clone().lerp(tip, 0.5);
        const len = origin.distanceTo(tip);

        // ── FIX: guard zero-length direction (causes NaN in quaternion) ───────
        if (len < 1e-6) return;

        const dir = tip.clone().sub(origin).normalize();

        // ── FIX: guard NaN in dir after normalize ────────────────────────────
        if (!isFinite(dir.x) || !isFinite(dir.y) || !isFinite(dir.z)) return;

        const dummy = new THREE.Object3D();
        dummy.position.copy(mid);
        dummy.scale.set(1, len, 1);
        dummy.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
        dummy.updateMatrix();

        // ── FIX: guard NaN in final matrix ───────────────────────────────────
        const elems = dummy.matrix.elements;
        if (elems.some(v => !isFinite(v))) return;

        this.mesh.setMatrixAt(i, dummy.matrix);
        this.ages[i] = 1.0;
        this.mesh.instanceMatrix.needsUpdate = true;
        this.count++;
    }

    tick() {
        let maxOp = 0;
        for (let i = 0; i < MAX_LASERS; i++) {
            if (this.ages[i] > 0) {
                this.ages[i] = Math.max(0, this.ages[i] - 0.012);
                if (this.ages[i] > maxOp) maxOp = this.ages[i];
            }
        }
        (this.mesh.material as THREE.MeshBasicMaterial).opacity = Math.max(0.1, maxOp);
    }

    dispose(scene: THREE.Scene) { scene.remove(this.mesh); }
}

export default function GaiaVoltGlobe() {
    const mountRef = useRef<HTMLDivElement>(null);
    const sceneRef = useRef<THREE.Scene | null>(null);
    const globeRef = useRef<THREE.Mesh | null>(null);
    const atmRef = useRef<THREE.Mesh | null>(null);
    const rendRef = useRef<THREE.WebGLRenderer | null>(null);
    const frameRef = useRef<number>(0);
    const poolRef = useRef<LaserPool | null>(null);
    const lastRef = useRef(0);
    const velRef = useRef({ x: 0, y: 0.0008 });
    const dragRef = useRef({ on: false, lx: 0, ly: 0 });
    const fpsRef = useRef({ frames: 0, last: 0 });
    const lastIdRef = useRef(0);

    const [idx, setIdx] = useState(0);
    const [co2, setCo2] = useState(0);
    const [acts, setActs] = useState(0);
    const [fps, setFps] = useState(60);
    const [backendLive, setBackendLive] = useState(false);
    const [nasaTemp, setNasaTemp] = useState<string>('API');
    const [ecoxLocked, setEcoxLocked] = useState('0.025');
    const [carbonRate, setCarbonRate] = useState<string>('');

    useEffect(() => {
        if (!mountRef.current) return;
        const W = mountRef.current.clientWidth || window.innerWidth;
        const H = mountRef.current.clientHeight || window.innerHeight;

        const scene = new THREE.Scene();
        sceneRef.current = scene;

        // Stars
        const sp = new Float32Array(8000);
        for (let i = 0; i < 8000; i++) sp[i] = (Math.random() - 0.5) * 500;
        const sg = new THREE.BufferGeometry();
        sg.setAttribute('position', new THREE.BufferAttribute(sp, 3));
        scene.add(new THREE.Points(sg, new THREE.PointsMaterial({ color: 0xffffff, size: 0.2 })));

        const loader = new THREE.TextureLoader();
        const earthTex = loader.load('/earth.jpg');
        earthTex.magFilter = THREE.LinearFilter;
        earthTex.minFilter = THREE.LinearMipmapLinearFilter;
        earthTex.anisotropy = 8;

        const globe = new THREE.Mesh(
            new THREE.SphereGeometry(1, isMobile ? 32 : 56, isMobile ? 32 : 56),
            new THREE.MeshPhongMaterial({
                map: earthTex,
                specular: new THREE.Color(0x111111),
                shininess: 25,
                color: new THREE.Color(0x334466),
            })
        );
        scene.add(globe);
        globeRef.current = globe;

        const atm = new THREE.Mesh(
            new THREE.SphereGeometry(1.13, 32, 32),
            new THREE.ShaderMaterial({
                vertexShader: ATM_VERT, fragmentShader: ATM_FRAG,
                blending: THREE.AdditiveBlending, side: THREE.BackSide,
                transparent: true, depthWrite: false,
            })
        );
        scene.add(atm);
        atmRef.current = atm;

        poolRef.current = new LaserPool(scene);

        scene.add(new THREE.AmbientLight(0x223344, 2.5));
        const sun = new THREE.DirectionalLight(0x5577ff, 3.5);
        sun.position.set(5, 3, 5);
        scene.add(sun);

        const cam = new THREE.PerspectiveCamera(45, W / H, 0.1, 1000);
        cam.position.set(0, 0, 2.8);

        const renderer = new THREE.WebGLRenderer({
            antialias: !isMobile, alpha: true, powerPreference: 'high-performance'
        });
        renderer.setSize(W, H);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, isMobile ? 1 : 2));
        renderer.setClearColor(0x020d18, 1);
        mountRef.current.appendChild(renderer.domElement);
        rendRef.current = renderer;

        const tick = (now: number) => {
            frameRef.current = requestAnimationFrame(tick);
            if (now - lastRef.current < FRAME_MS) return;
            lastRef.current = now;

            fpsRef.current.frames++;
            if (now - fpsRef.current.last > 1000) {
                setFps(fpsRef.current.frames);
                if (fpsRef.current.frames < 25) renderer.setPixelRatio(1);
                fpsRef.current = { frames: 0, last: now };
            }

            velRef.current.y *= 0.94;
            velRef.current.x *= 0.94;
            globe.rotation.y += velRef.current.y;
            globe.rotation.x += velRef.current.x;
            globe.rotation.x = Math.max(-0.45, Math.min(0.45, globe.rotation.x));
            atm.rotation.copy(globe.rotation);

            poolRef.current?.tick();

            // ── FIX 3: try/catch around render — prevents white screen on NaN ─
            try {
                renderer.render(scene, cam);
            } catch (e) {
                console.warn('Globe render error (caught):', e);
            }
        };
        requestAnimationFrame(tick);

        const down = (e: MouseEvent | TouchEvent) => {
            const x = 'touches' in e ? e.touches[0].clientX : e.clientX;
            const y = 'touches' in e ? e.touches[0].clientY : e.clientY;
            dragRef.current = { on: true, lx: x, ly: y };
            velRef.current = { x: 0, y: 0 };
        };
        const move = (e: MouseEvent | TouchEvent) => {
            if (!dragRef.current.on) return;
            const x = 'touches' in e ? e.touches[0].clientX : e.clientX;
            const y = 'touches' in e ? e.touches[0].clientY : e.clientY;
            velRef.current = { x: (y - dragRef.current.ly) * 0.004, y: (x - dragRef.current.lx) * 0.004 };
            dragRef.current = { on: true, lx: x, ly: y };
        };
        const up = () => { dragRef.current.on = false; };

        const el = renderer.domElement;
        el.addEventListener('mousedown', down);
        el.addEventListener('mousemove', move);
        el.addEventListener('mouseup', up);
        el.addEventListener('touchstart', down, { passive: true });
        el.addEventListener('touchmove', move, { passive: true });
        el.addEventListener('touchend', up);

        const onResize = () => {
            if (!mountRef.current) return;
            const w = mountRef.current.clientWidth;
            const h = mountRef.current.clientHeight;
            if (!w || !h) return;   // FIX: skip if container not mounted yet
            cam.aspect = w / h;
            cam.updateProjectionMatrix();
            renderer.setSize(w, h);
        };
        window.addEventListener('resize', onResize);

        return () => {
            window.removeEventListener('resize', onResize);
            cancelAnimationFrame(frameRef.current);
            poolRef.current?.dispose(scene);
            renderer.dispose();
            if (mountRef.current?.contains(renderer.domElement)) {
                mountRef.current.removeChild(renderer.domElement);
            }
        };
    }, []);

    useEffect(() => {
        const a = ACTIONS[idx];
        if (!a) return;
        poolRef.current?.add(a.lat, a.lon);
        setCo2(p => parseFloat((p + a.co2).toFixed(2)));
        setActs(p => p + 1);
    }, [idx]);

    useEffect(() => {
        const t = setInterval(() => setIdx(i => (i + 1) % ACTIONS.length), 2500);
        return () => clearInterval(t);
    }, []);

    useEffect(() => {
        const poll = async () => {
            const stats = await fetchStats();
            if (stats) {
                setBackendLive(true);
                if (stats.total_actions > 0) {
                    setCo2(stats.total_co2_kg);
                    setActs(stats.total_actions);
                }
            }

            const recent = await fetchRecentActions();
            if (recent?.actions?.length > 0) {
                const latest = recent.actions[0];
                if (latest.id !== lastIdRef.current) {
                    lastIdRef.current = latest.id;
                    // FIX: safe fallback for lat/lon from backend
                    const lat = typeof latest.lat === 'number' && isFinite(latest.lat) ? latest.lat : 24.86;
                    const lon = typeof latest.lon === 'number' && isFinite(latest.lon) ? latest.lon : 67.00;
                    poolRef.current?.add(lat, lon);
                }
            }

            const globeData = await fetchGlobeData();
            if (globeData) {
                if (globeData.oracle?.temp_c != null) setNasaTemp(`${globeData.oracle.temp_c}°C`);
                if (globeData.oracle?.carbon_rate != null) setCarbonRate(`$${globeData.oracle.carbon_rate}/t`);
                if (globeData.ecox_locked != null) setEcoxLocked(globeData.ecox_locked.toFixed(4));
                if (globeData.total_co2 > 0) setCo2(globeData.total_co2);
                if (globeData.total_actions > 0) setActs(globeData.total_actions);
            }
        };
        poll();
        const t = setInterval(poll, 30000);
        return () => clearInterval(t);
    }, []);

    const action = ACTIONS[idx];

    return (
        <div className="relative w-full h-screen overflow-hidden"
            style={{ background: '#020d18', fontFamily: "'Courier New', monospace" }}>

            <div ref={mountRef} className="absolute inset-0" />

            <div className="absolute top-16 right-4 z-20 flex flex-col items-end gap-1">
                <div className="text-[9px] tracking-widest"
                    style={{ color: fps < 30 ? '#ff4444' : '#00ff88', opacity: 0.5 }}>
                    {fps} FPS
                </div>
                <div className="text-[9px] tracking-widest"
                    style={{ color: backendLive ? '#00ff88' : '#ff6644', opacity: 0.5 }}>
                    {backendLive ? '● LIVE' : '○ OFFLINE'}
                </div>
            </div>

            <motion.div
                initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 1 }}
                className="absolute top-0 left-0 right-0 flex items-center justify-between px-6 py-4 z-10"
                style={{ background: 'linear-gradient(to bottom, rgba(2,13,24,0.9), transparent)' }}
            >
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: '#00ff88' }} />
                    <span className="font-bold tracking-widest" style={{ color: '#00ff88', fontSize: isMobile ? '14px' : '18px' }}>
                        GAIA<span style={{ color: '#ffaa00' }}>VOLT</span>
                    </span>
                    <span className="text-[10px] tracking-widest" style={{ color: 'rgba(0,255,136,0.4)' }}>
                        PROOF OF PLANET
                    </span>
                </div>
                <div className="flex gap-3 text-[10px] tracking-widest" style={{ color: 'rgba(0,255,136,0.5)' }}>
                    <span style={{ color: '#00ff88' }}>POLYGON ✓</span>
                    <span>•</span>
                    <span style={{ color: nasaTemp !== 'API' ? '#00ccff' : 'rgba(0,255,136,0.4)' }}>
                        {nasaTemp !== 'API' ? `🌡️ ${nasaTemp} LIVE` : 'NASA API...'}
                    </span>
                    <span>•</span>
                    <span style={{ color: carbonRate ? '#ffaa00' : 'rgba(0,255,136,0.4)' }}>
                        {carbonRate ? `💰 ${carbonRate} LIVE` : 'IPCC AR6...'}
                    </span>
                </div>
            </motion.div>

            <motion.div
                initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 1, delay: 0.3 }}
                className="absolute left-4 top-1/2 -translate-y-1/2 z-10 flex flex-col gap-2"
            >
                {[
                    { label: 'CO₂ SAVED', value: `${co2} kg`, color: '#00ff88' },
                    { label: 'ACTIONS', value: `${acts}`, color: '#00ccff' },
                    { label: 'LIVE CITY', value: action.city, color: '#ffaa00' },
                ].map(s => (
                    <div key={s.label} className="px-3 py-2 rounded-lg backdrop-blur"
                        style={{ border: `1px solid ${s.color}30`, background: 'rgba(2,13,24,0.85)' }}>
                        <div className="text-[8px] tracking-widest" style={{ color: s.color + '60' }}>{s.label}</div>
                        <div className="font-bold" style={{ color: s.color, fontSize: isMobile ? '12px' : '15px' }}>{s.value}</div>
                    </div>
                ))}
            </motion.div>

            <motion.div
                initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 1, delay: 0.5 }}
                className="absolute right-4 top-1/2 -translate-y-1/2 z-10"
                style={{ width: isMobile ? '140px' : '200px' }}
            >
                <AnimatePresence mode="wait">
                    <motion.div key={action.id}
                        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
                        className="rounded-xl p-4 backdrop-blur"
                        style={{ border: '1px solid rgba(0,255,136,0.2)', background: 'rgba(2,13,24,0.9)' }}
                    >
                        <div className="text-[8px] tracking-widest mb-1" style={{ color: 'rgba(0,255,136,0.5)' }}>
                            {backendLive ? '🟢 LIVE' : 'ACTION'}
                        </div>
                        <div style={{ fontSize: isMobile ? '20px' : '28px' }} className="mb-1">
                            {ICONS[action.type] || '🌱'}
                        </div>
                        <div className="font-bold" style={{ color: '#00ff88', fontSize: isMobile ? '13px' : '16px' }}>
                            {action.city}
                        </div>
                        <div className="text-[9px] tracking-widest" style={{ color: 'rgba(0,255,136,0.5)' }}>
                            {action.country}
                        </div>
                        <div className="text-[9px] mt-1 tracking-widest" style={{ color: 'rgba(0,255,136,0.4)' }}>
                            {action.type.replace(/_/g, ' ').toUpperCase()}
                        </div>
                        <div className="mt-2 pt-2 grid grid-cols-2 gap-1"
                            style={{ borderTop: '1px solid rgba(0,255,136,0.1)' }}>
                            <div>
                                <div className="text-[7px] tracking-widest" style={{ color: 'rgba(0,255,136,0.4)' }}>CO₂</div>
                                <div className="font-bold text-[11px]" style={{ color: '#00ff88' }}>{action.co2}kg</div>
                            </div>
                            <div>
                                <div className="text-[7px] tracking-widest" style={{ color: 'rgba(0,204,255,0.4)' }}>AI</div>
                                <div className="font-bold text-[11px]" style={{ color: '#00ccff' }}>{action.conf}%</div>
                            </div>
                        </div>
                    </motion.div>
                </AnimatePresence>
            </motion.div>

            <motion.div
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 1, delay: 0.7 }}
                className="absolute bottom-4 left-1/2 -translate-x-1/2 z-10 w-full px-4"
                style={{ maxWidth: '420px' }}
            >
                <div className="flex items-center justify-center gap-3 px-5 py-2 rounded-full"
                    style={{ border: '1px solid rgba(255,170,0,0.3)', background: 'rgba(2,13,24,0.9)' }}>
                    <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: '#ffaa00' }} />
                    <span className="text-[10px] tracking-widest whitespace-nowrap" style={{ color: 'rgba(255,170,0,0.7)' }}>
                        QUANTUM-LOCK 2050
                    </span>
                    <span className="font-bold text-[11px] whitespace-nowrap" style={{ color: '#ffaa00' }}>
                        {ecoxLocked} GAIAX LOCKED
                    </span>
                    <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: '#ffaa00' }} />
                </div>
            </motion.div>

        </div>
    );
}