import React from 'react';

function toCssBackground(rgb: [number, number, number]): string {
  return `#${rgb.map(val => val.toString(16).padStart(2, '0')).join('')};`;
}

function moveToFront<T>(array: T[], index: number): T[] {
  if (index >= array.length) {
    throw new Error("Index out of bounds");
  }
  const [item] = array.splice(index, 1);
  array.unshift(item!);
  return array;
}

interface SwatchProps {
  position: number;
}

const Swatch: React.FC<SwatchProps> = ({ position }) => {

  const background_color = '#ff0000';


  return (
    <div
      className={'w-24 h-8 rounded-full justify-center'}
      style={{ backgroundColor: background_color }}
      //onClick={onClick}
    >
    </div>
  );
};

export default Swatch;
