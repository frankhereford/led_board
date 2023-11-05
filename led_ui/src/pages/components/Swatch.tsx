import React, { useContext, useEffect, useState } from 'react';
import { AppContext } from '~/pages/contexts/AppContext';

function toCssBackground(rgb: [number, number, number]): string {
  return `#${rgb.map(val => val.toString(16).padStart(2, '0')).join('')}`;
}

interface SwatchProps {
  position: number;
}

const Swatch: React.FC<SwatchProps> = ({ position }) => {
  const { colorArrays, setColorArrays, activeSwatch, setActiveSwatch } = useContext(AppContext);
  const [backgroundColor, setBackgroundColor] = useState('#000000');

  useEffect(() => {
    const colorArray = colorArrays[position];
    if (colorArray && colorArray.length === 3) {
      const newColor = toCssBackground(colorArray as [number, number, number]);
      setBackgroundColor(newColor);
    }
  }, [colorArrays, position]);

  const handleClick = () => {
    setActiveSwatch(position);
  };

  return (
    <div
      className={`mb-4 mx-1 w-24 h-8 rounded-full justify-center ${activeSwatch === position ? 'ring-4 ring-blue-500' : ''}`}
      style={{ backgroundColor: backgroundColor }}
      onClick={handleClick}
    >
    </div>
  );
};

export default Swatch;
