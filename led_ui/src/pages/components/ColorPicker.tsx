import React from 'react';
import { useContext } from 'react';
import { ChromePicker } from 'react-color';
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

    // use setColorArrays to update the colorArrays state variable in the activeSwatch position
  };

  return (
    <div className="mb-4">
      <ChromePicker
        color={ arrayToRgbColor(colorArrays[activeSwatch]) }
        onChangeComplete={ handleChangeComplete }
      />
    </div>
  )
}

export default ColorPicker;