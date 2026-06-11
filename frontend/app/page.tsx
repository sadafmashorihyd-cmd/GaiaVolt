'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import EcoXGlobe from './EcoGlobe';
import Link from 'next/link';

export default function Home() {
    const router = useRouter();
    useEffect(() => {
        const token = localStorage.getItem('gv_token');
        if (!token) router.push('/auth');
    }, [router]);
    return (
        <div style={{ position: 'relative' }}>
            <EcoXGlobe />
            <Link href="/verify" style={{ position: 'fixed', bottom: 32, right: 32, padding: '14px 24px', borderRadius: 14, background: 'linear-gradient(135deg, #16a34a, #22c55e)', color: '#fff', fontWeight: 700, fontSize: 15, textDecoration: 'none', boxShadow: '0 0 24px #22c55e55', zIndex: 1000 }}>⚡ Verify & Earn</Link>
            <Link href="/nfts" style={{ position: 'fixed', bottom: 148, right: 32, padding: '12px 20px', borderRadius: 14, background: 'linear-gradient(135deg, #78350f, #d97706)', color: '#fff', fontWeight: 700, fontSize: 13, textDecoration: 'none', boxShadow: '0 0 20px #d9770633', zIndex: 1000 }}>🎨 NFTs</Link>
            <Link href="/bridges" style={{ position: 'fixed', bottom: 90, right: 32, padding: '12px 20px', borderRadius: 14, background: 'linear-gradient(135deg, #92400e, #f59e0b)', color: '#fff', fontWeight: 700, fontSize: 13, textDecoration: 'none', boxShadow: '0 0 20px #f59e0b33', zIndex: 1000 }}>🏪 Eco Store</Link>
            <Link href="/evolution" style={{ position: 'fixed', bottom: 32, left: 32, padding: '14px 24px', borderRadius: 14, background: 'linear-gradient(135deg, #166534, #16a34a)', color: '#fff', fontWeight: 700, fontSize: 15, textDecoration: 'none', boxShadow: '0 0 24px #22c55e33', zIndex: 1000 }}>🌱 My Journey</Link>
        </div>
    );
}