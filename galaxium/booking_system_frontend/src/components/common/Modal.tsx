// Modified for Earshot (IBM Bob 2.0 Hackathon, Sept 2026): accessibility fixes; see galaxium/MODIFICATIONS.md
import type { ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { useEffect, useRef } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

export const Modal = ({ isOpen, onClose, title, children, size = 'md' }: ModalProps) => {
  const dialogRef = useRef<HTMLDivElement>(null);
  const titleId = useRef(`modal-title-${Math.random().toString(36).slice(2)}`).current;
  const returnFocusRef = useRef<HTMLElement | null>(null);

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-2xl',
    lg: 'max-w-4xl',
  };

  // Close on escape key; trap focus inside dialog
  useEffect(() => {
    const FOCUSABLE = 'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { onClose(); return; }
      if (e.key !== 'Tab') return;

      const el = dialogRef.current;
      if (!el) return;
      const focusable = Array.from(el.querySelectorAll<HTMLElement>(FOCUSABLE)).filter(n => n.tabIndex !== -1 || n === el);
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === first) { e.preventDefault(); last.focus(); }
      } else {
        if (document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    };
    
    if (isOpen) {
      returnFocusRef.current = document.activeElement as HTMLElement;
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
      // Defer focus so the motion.div is in the DOM before we focus it
      setTimeout(() => dialogRef.current?.focus(), 0);
    } else {
      returnFocusRef.current?.focus();
      returnFocusRef.current = null;
    }
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40"
          />
          
          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-start justify-center p-4 pt-20 overflow-y-auto">
            <motion.div
              ref={dialogRef}
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className={`bg-space-dark/95 backdrop-blur-xl border-2 border-cosmic-purple/30 rounded-2xl shadow-2xl shadow-cosmic-purple/20 w-full ${sizeClasses[size]} my-8 p-6`}
              role="dialog"
              aria-modal="true"
              aria-labelledby={title ? titleId : undefined}
              tabIndex={-1}
            >
              {/* Header */}
              {title && (
                <div className="flex items-center justify-between mb-6 pb-4 border-b border-cosmic-purple/20">
                  <h2 id={titleId} className="text-2xl font-bold bg-cosmic-gradient bg-clip-text text-transparent">{title}</h2>
                  <button
                    onClick={onClose}
                    className="text-star-white/70 hover:text-cosmic-purple transition-colors p-1 hover:bg-white/5 rounded-lg"
                    aria-label="Close modal"
                  >
                    <X size={24} />
                  </button>
                </div>
              )}
              
              {/* Content */}
              <div>{children}</div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};

// Made with Bob
