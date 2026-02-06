import { useState, useEffect } from "react";

const phrases = [
  "Frensei structures every stage of the PhD journey.",
  "It strengthens supervision and reduces risk.",
  "It connects researchers to real opportunities.",
  "It transforms inefficiency into continuity.",
];

export const TypingAnimation = () => {
  const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0);
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(true);
  const [showCursor, setShowCursor] = useState(true);

  useEffect(() => {
    const currentPhrase = phrases[currentPhraseIndex];
    
    if (isTyping) {
      if (displayedText.length < currentPhrase.length) {
        const timeout = setTimeout(() => {
          setDisplayedText(currentPhrase.slice(0, displayedText.length + 1));
        }, 45);
        return () => clearTimeout(timeout);
      } else {
        const timeout = setTimeout(() => {
          setIsTyping(false);
        }, 2000);
        return () => clearTimeout(timeout);
      }
    } else {
      if (displayedText.length > 0) {
        const timeout = setTimeout(() => {
          setDisplayedText(displayedText.slice(0, -1));
        }, 30);
        return () => clearTimeout(timeout);
      } else {
        setCurrentPhraseIndex((prev) => (prev + 1) % phrases.length);
        setIsTyping(true);
      }
    }
  }, [displayedText, isTyping, currentPhraseIndex]);

  useEffect(() => {
    const interval = setInterval(() => {
      setShowCursor((prev) => !prev);
    }, 400);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-[#111111] border border-[#DB5614] rounded-lg p-6 font-mono text-white text-sm md:text-base min-h-[80px] flex items-center">
      <span>
        {displayedText}
        <span className={`${showCursor ? "opacity-100" : "opacity-0"} transition-opacity`}>
          _
        </span>
      </span>
    </div>
  );
};
