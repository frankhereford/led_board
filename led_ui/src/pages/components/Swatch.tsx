import React from 'react';
import { inks } from "~/pages/index";
import { signal, computed } from "@preact/signals-react";


function toTailwindBgClass(rgb: [number, number, number]): string {
  return `bg-[#${rgb.map((val) => val.toString(16).padStart(2, '0')).join('')}]`;
}

function toCssBackground(rgb: [number, number, number]): string {
  return `#${rgb.map(val => val.toString(16).padStart(2, '0')).join('')};`;
}

interface SwatchProps {
  position: number;
}

const Swatch: React.FC<SwatchProps> = ({ position }) => {

  const color = computed(() => inks.value[position]!);
  const background_color = computed(() => toCssBackground(inks.value[position]));

  return (
    <div
      className={'w-16 h-8 rounded-full'}
      style={{ backgroundColor: background_color.value }}
    >
    </div>
  );
};

export default Swatch;
