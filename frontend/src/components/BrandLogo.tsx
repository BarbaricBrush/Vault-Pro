import React from 'react';
import Image from 'next/image';

interface BrandLogoProps {
  className?: string;
  showText?: boolean;
}

export default function BrandLogo({ className, showText = true }: BrandLogoProps) {
  return (
    <div className={`relative ${className} flex items-center justify-center`}>
      <Image 
        src="/logosvg.svg" 
        alt="Vault Pro Logo" 
        fill
        className={`object-contain ${showText ? '' : 'scale-150'}`} // Zoom in slightly for icon-only mode if needed
        priority
      />
    </div>
  );
}
