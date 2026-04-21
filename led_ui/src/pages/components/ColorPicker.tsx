import React from 'react';
import { useContext } from 'react';
import { TwitterPicker } from 'react-color';
import { AppContext } from '~/pages/contexts/AppContext';

function arrayToRgbColor(array: [number, number, number]): { r: number; g: number; b: number } {
  const [r, g, b] = array;
  return { r, g, b };
}

function hexToRgbArray(hex: string): [number, number, number] | null {
  const match = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return match ? [parseInt(match[1], 16), parseInt(match[2], 16), parseInt(match[3], 16)] : null;
}

const replaceArrayValue = (array, index, newValue) => {
  return [
    ...array.slice(0, index), // Elements before the index
    newValue,                 // New value at the index
    ...array.slice(index + 1) // Elements after the index
  ];
};


const ColorPicker: React.FC = ({ }) => {
  const { colorArrays, setColorArrays, isMouseDown, activeSwatch } = useContext(AppContext);

  const handleChangeComplete = (color) => {
    console.log(hexToRgbArray(color.hex))
    setColorArrays(replaceArrayValue(colorArrays, activeSwatch, hexToRgbArray(color.hex)));
  };

  return (
    <div className="mb-4">
      <TwitterPicker
        height={ 570 }
        width={ 387 }
        triangle="hide"

        colors={['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#FF6900', '#FCB900', '#7BDCB5', '#00D084', '#8ED1FC', '#0693E3', '#ABB8C3', '#EB144C', '#F78DA7', '#9900EF']}
        color={ arrayToRgbColor(colorArrays[activeSwatch]) }
        onChangeComplete={ handleChangeComplete }
      />
    </div>
  )
}

export default ColorPicker;