// Modified for Earshot (IBM Bob 2.0 Hackathon, Sept 2026): accessibility fixes; see galaxium/MODIFICATIONS.md
import { useEffect, useRef, useState } from 'react';

export const Starfield = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const pausedRef = useRef(false);
  const animationFrameIdRef = useRef<number>(0);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const setCanvasSize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    setCanvasSize();
    window.addEventListener('resize', setCanvasSize);

    // Create stars
    const stars: Array<{
      x: number;
      y: number;
      radius: number;
      opacity: number;
      twinkleSpeed: number;
      twinklePhase: number;
    }> = [];

    const numStars = 200;
    for (let i = 0; i < numStars; i++) {
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 1.5 + 0.5,
        opacity: Math.random(),
        twinkleSpeed: Math.random() * 0.02 + 0.01,
        twinklePhase: Math.random() * Math.PI * 2,
      });
    }

    // Animation loop
    const animate = () => {
      if (!pausedRef.current) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw stars
        stars.forEach((star) => {
          // Twinkle effect
          star.twinklePhase += star.twinkleSpeed;
          const twinkle = Math.sin(star.twinklePhase) * 0.5 + 0.5;
          const opacity = star.opacity * twinkle;

          ctx.beginPath();
          ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`;
          ctx.fill();

          // Slow drift
          star.y += 0.1;
          if (star.y > canvas.height) {
            star.y = 0;
            star.x = Math.random() * canvas.width;
          }
        });
      }

      animationFrameIdRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', setCanvasSize);
      cancelAnimationFrame(animationFrameIdRef.current);
    };
  }, []);

  const togglePause = () => {
    pausedRef.current = !pausedRef.current;
    setPaused(pausedRef.current);
  };

  return (
    <>
      <canvas
        ref={canvasRef}
        className="fixed inset-0 pointer-events-none z-0"
        style={{ background: 'linear-gradient(to bottom, #030712, #0A1929)' }}
      />
      <button
        onClick={togglePause}
        aria-label={paused ? 'Resume animation' : 'Pause animation'}
        className="fixed bottom-4 right-4 z-50 bg-white/10 hover:bg-white/20 text-white text-xs px-3 py-1 rounded focus:outline-none focus:ring-2 focus:ring-white"
      >
        {paused ? 'Resume animation' : 'Pause animation'}
      </button>
    </>
  );
};

// Made with Bob
