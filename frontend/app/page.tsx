'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import EcoXGlobe from './EcoGlobe';
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
    "https://rjqxdsrhgnydhtlegyxx.supabase.co",
    "sb_publishable_yxkdO7v2GNL4TAzJ1lbb_g_wXjYxLQY"
);

export default function Home() {
    const router = useRouter();
    const [user, setUser] = useState(null);
    const [showMenu, setShowMenu] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('gv_token');
        if (!token) {
            router.push('/auth');
            return;
        }
        try {
            const userData = JSON.parse(localStorage.getItem('gv_user') || '{}');
            setUser(userData);
        } catch (e) { }
    }, [router]);

    const handleSignout = async () => {
        await supabase.auth.signOut();
        localStorage.removeItem('gv_token');
        localStorage.removeItem('gv_user');
        localStorage.removeItem('gv_biometric_id');
        localStorage.removeItem('gv_biometric_email');
        localStorage.removeItem('gv_biometric_password');
        router.push('/auth');
    };

    return (
        <div style={{ position: 'relative', width: '100%', height: '100vh', overflow: 'hidden' }}>
            {/* Top bar with user info and signout */}
            <div style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                zIndex: 1000,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '10px 16px',
                background: 'rgba(0,0,0,0.5)',
                backdropFilter: 'blur(8px)',
                borderBottom: '1px solid rgba(0,255,136,0.15)',
            }}>
                {/* Logo */}
                <div style={{ color: '#00ff88', fontSize: '14px', fontWeight: 'bold', fontFamily: 'monospace', letterSpacing: '2px' }}>
                    🌍 GAIAVOLT
                </div>

                {/* User + Menu */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    {user?.name && (
                        <span style={{ color: 'rgba(0,255,136,0.7)', fontSize: '12px', fontFamily: 'monospace' }}>
                            {user.name}
                        </span>
                    )}
                    <button
                        onClick={() => setShowMenu(!showMenu)}
                        style={{
                            background: 'rgba(0,255,136,0.1)',
                            border: '1px solid rgba(0,255,136,0.3)',
                            borderRadius: '6px',
                            color: '#00ff88',
                            fontSize: '18px',
                            width: '36px',
                            height: '36px',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        ☰
                    </button>
                </div>
            </div>

            {/* Dropdown Menu */}
            {showMenu && (
                <div style={{
                    position: 'fixed',
                    top: '56px',
                    right: '16px',
                    zIndex: 1001,
                    background: 'rgba(5,15,10,0.97)',
                    border: '1px solid rgba(0,255,136,0.3)',
                    borderRadius: '10px',
                    padding: '8px',
                    minWidth: '160px',
                    backdropFilter: 'blur(10px)',
                }}>
                    <button
                        onClick={() => { router.push('/verify'); setShowMenu(false); }}
                        style={{ width: '100%', padding: '10px 14px', background: 'transparent', border: 'none', color: '#00ff88', fontSize: '13px', fontFamily: 'monospace', cursor: 'pointer', textAlign: 'left', borderRadius: '6px' }}
                    >
                        📸 Verify Action
                    </button>
                    <button
                        onClick={() => { router.push('/evolution'); setShowMenu(false); }}
                        style={{ width: '100%', padding: '10px 14px', background: 'transparent', border: 'none', color: '#00ff88', fontSize: '13px', fontFamily: 'monospace', cursor: 'pointer', textAlign: 'left', borderRadius: '6px' }}
                    >
                        🌱 My Evolution
                    </button>
                    <div style={{ borderTop: '1px solid rgba(0,255,136,0.15)', margin: '6px 0' }} />
                    <button
                        onClick={handleSignout}
                        style={{ width: '100%', padding: '10px 14px', background: 'transparent', border: 'none', color: '#ff6666', fontSize: '13px', fontFamily: 'monospace', cursor: 'pointer', textAlign: 'left', borderRadius: '6px' }}
                    >
                        🚪 Sign Out
                    </button>
                </div>
            )}

            {/* Close menu on outside click */}
            {showMenu && (
                <div
                    onClick={() => setShowMenu(false)}
                    style={{ position: 'fixed', inset: 0, zIndex: 999 }}
                />
            )}

            {/* Globe */}
            <EcoXGlobe />
        </div>
    );
}