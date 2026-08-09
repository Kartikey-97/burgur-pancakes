"use client";

import { useEffect, useRef } from "react";

export default function BackgroundParticles() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const cvs = canvasRef.current;
    if (!cvs) return;
    const ctx = cvs.getContext("2d");
    if (!ctx) return;

    let W = 0, H = 0;
    let animationFrameId: number;

    const resize = () => {
      W = cvs.width = window.innerWidth;
      H = cvs.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    const pts = Array.from({ length: 8 }, () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      r: Math.random() * 200 + 100, // Large orbs
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      color: `rgba(${Math.floor(Math.random()*100 + 155)}, ${Math.floor(Math.random()*100 + 155)}, 255, 0.4)`
    }));

    const draw = () => {
      ctx.clearRect(0, 0, W, H);
      
      // Soft gradient background
      const gradient = ctx.createLinearGradient(0, 0, W, H);
      gradient.addColorStop(0, '#f8fafc');
      gradient.addColorStop(1, '#e2e8f0');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, W, H);

      // Draw floating orbs
      pts.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        
        // Radial gradient for softness
        const rg = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r);
        rg.addColorStop(0, p.color);
        rg.addColorStop(1, 'rgba(255,255,255,0)');
        
        ctx.fillStyle = rg;
        ctx.fill();
        
        p.x += p.vx;
        p.y += p.vy;
        
        // Bounce off walls
        if (p.x < -p.r) p.vx *= -1;
        if (p.x > W + p.r) p.vx *= -1;
        if (p.y < -p.r) p.vy *= -1;
        if (p.y > H + p.r) p.vy *= -1;
      });
      animationFrameId = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return <canvas id="particles-canvas" ref={canvasRef}></canvas>;
}
