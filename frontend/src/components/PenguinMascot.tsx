import { useEffect, useState } from "react";
import penguinMascot from "@/assets/penguin-mascot.png";
import { removeBackground, loadImage } from "@/lib/backgroundRemoval";

interface PenguinMascotProps {
  size?: number;
  className?: string;
}

export const PenguinMascot = ({ size = 48, className = "" }: PenguinMascotProps) => {
  const [processedImage, setProcessedImage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const processImage = async () => {
      setIsProcessing(true);
      try {
        // Load the image directly (static asset, no API call needed)
        const img = new Image();
        img.src = penguinMascot;
        await new Promise((resolve, reject) => {
          img.onload = resolve;
          img.onerror = reject;
        });
        const imageElement = img;
        
        // Remove background
        const resultBlob = await removeBackground(imageElement);
        const url = URL.createObjectURL(resultBlob);
        setProcessedImage(url);
      } catch (error) {
        console.error('Failed to process penguin mascot:', error);
        // Fallback to original image if processing fails
        setProcessedImage(penguinMascot);
      } finally {
        setIsProcessing(false);
      }
    };

    processImage();

    return () => {
      if (processedImage) {
        URL.revokeObjectURL(processedImage);
      }
    };
  }, []);

  if (isProcessing || !processedImage) {
    return (
      <div 
        className={`rounded-full bg-white/10 flex items-center justify-center animate-pulse ${className}`}
        style={{ width: size, height: size }}
      >
        <span className="text-2xl">🐧</span>
      </div>
    );
  }

  return (
    <img
      src={processedImage}
      alt="Frensei Penguin Mascot"
      className={`object-contain ${className}`}
      style={{ width: size, height: size }}
    />
  );
};
