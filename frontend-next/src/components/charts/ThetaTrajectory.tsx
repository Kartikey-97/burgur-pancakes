"use client";

import { useEffect, useRef } from "react";

export default function ThetaTrajectory({ history }: { history: number[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const cvs = canvasRef.current;
    if (!cvs || !history || history.length < 2) return;
    const ctx = cvs.getContext("2d");
    if (!ctx) return;

    const W = cvs.width, H = cvs.height;
    
    const minT = -2, maxT = 2;
    const range = maxT - minT;
    const padX = 10, padY = 10;
    const useW = W - padX * 2, useH = H - padY * 2;
    
    const getX = (i: number) => padX + (i / (history.length - 1)) * useW;
    const getY = (val: number) => {
      const v = Math.max(minT, Math.min(maxT, val));
      return H - padY - ((v - minT) / range) * useH;
    };

    let prog = 0;
    let animationFrameId: number;

    const frame = () => {
      prog = Math.min(prog + 0.04, 1);
      const ease = 1 - Math.pow(1 - prog, 3);
      ctx.clearRect(0, 0, W, H);
      
      // Draw center line (theta = 0)
      ctx.beginPath();
      ctx.moveTo(padX, getY(0));
      ctx.lineTo(W - padX, getY(0));
      ctx.strokeStyle = "rgba(255,255,255,0.08)";
      ctx.lineWidth = 1;
      ctx.stroke();
      
      const maxIdx = Math.floor(ease * (history.length - 1));
      const subProg = ease * (history.length - 1) - maxIdx;
      
      ctx.beginPath();
      for (let i = 0; i <= maxIdx; i++) {
        if (i === 0) ctx.moveTo(getX(i), getY(history[i]));
        else ctx.lineTo(getX(i), getY(history[i]));
      }
      
      if (maxIdx < history.length - 1) {
        const x = getX(maxIdx) + (getX(maxIdx + 1) - getX(maxIdx)) * subProg;
        const y = getY(history[maxIdx]) + (getY(history[maxIdx + 1]) - getY(history[maxIdx])) * subProg;
        ctx.lineTo(x, y);
      }
      
      ctx.strokeStyle = "#00d4aa";
      ctx.lineWidth = 2;
      ctx.stroke();
      
      // Draw points
      for (let i = 0; i <= maxIdx; i++) {
        ctx.beginPath();
        ctx.arc(getX(i), getY(history[i]), 3, 0, Math.PI * 2);
        ctx.fillStyle = "#00d4aa";
        ctx.fill();
      }
      
      if (prog < 1) animationFrameId = requestAnimationFrame(frame);
    };

    const timeoutId = setTimeout(() => {
      animationFrameId = requestAnimationFrame(frame);
    }, 450);

    return () => {
      clearTimeout(timeoutId);
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, [history]);

  return <canvas ref={canvasRef} width={280} height={80}></canvas>;
}
