"use client";

import { useEffect, useRef } from "react";

export default function RadarChart({ scores }: { scores: Record<string, number> }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const cvs = canvasRef.current;
    if (!cvs || !scores) return;
    const ctx = cvs.getContext("2d");
    if (!ctx) return;

    const topics = Object.keys(scores);
    const N = topics.length;
    if (N < 3) return;

    const W = cvs.width, H = cvs.height;
    const cx = W / 2, cy = H / 2;
    const R = Math.min(cx, cy) - 25;

    let prog = 0;
    let animationFrameId: number;

    const frame = () => {
      prog = Math.min(prog + 0.04, 1);
      const ease = 1 - Math.pow(1 - prog, 3);
      ctx.clearRect(0, 0, W, H);

      // Grid
      ctx.strokeStyle = "rgba(255,255,255,0.08)";
      ctx.lineWidth = 1;
      for (let l = 1; l <= 4; l++) {
        const r = (R / 4) * l;
        ctx.beginPath();
        for (let i = 0; i < N; i++) {
          const a = (Math.PI * 2 * i) / N - Math.PI / 2;
          const x = cx + Math.cos(a) * r;
          const y = cy + Math.sin(a) * r;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.stroke();
      }
      
      // Axes
      for (let i = 0; i < N; i++) {
        const a = (Math.PI * 2 * i) / N - Math.PI / 2;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(cx + Math.cos(a) * R, cy + Math.sin(a) * R);
        ctx.stroke();
      }

      // Shape
      ctx.beginPath();
      for (let i = 0; i < N; i++) {
        const a = (Math.PI * 2 * i) / N - Math.PI / 2;
        const val = scores[topics[i]] || 0;
        const r = (R / 4) * val * ease;
        const x = cx + Math.cos(a) * r;
        const y = cy + Math.sin(a) * r;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();

      const grad = ctx.createLinearGradient(0, 0, W, H);
      grad.addColorStop(0, "rgba(108,99,255,0.4)");
      grad.addColorStop(1, "rgba(0,212,170,0.4)");
      ctx.fillStyle = grad;
      ctx.fill();
      ctx.strokeStyle = "#00d4aa";
      ctx.lineWidth = 2;
      ctx.stroke();

      if (prog < 1) animationFrameId = requestAnimationFrame(frame);
    };
    
    // Slight delay before animating
    const timeoutId = setTimeout(() => {
      animationFrameId = requestAnimationFrame(frame);
    }, 450);

    return () => {
      clearTimeout(timeoutId);
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, [scores]);

  return <canvas ref={canvasRef} width={280} height={280}></canvas>;
}
