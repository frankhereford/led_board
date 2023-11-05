import React, { useEffect, useState } from 'react';

import { useContext } from 'react';
import { AppContext } from '~/pages/contexts/AppContext';

import { api } from "~/utils/api";

interface SquareProps {
  x: number;
  y: number;
}

const Square: React.FC<SquareProps> = ({ x, y }) => {
  const setColor = api.square.color.useMutation({});
  const [squareColor, setSquareColor] = useState<number[]>([0,0,0]);
  const { colorArrays, isMouseDown, activeSwatch } = useContext(AppContext);

  useEffect(() => {
    setColor.mutate({ x: x, y: y, color: squareColor })
  }, [squareColor]);

  const handleMouseEnter = () => {
    if (isMouseDown) {
      setSquareColor(colorArrays[activeSwatch]!);
    }
  };

  return (
    <div
      style={{
        width: '20px',
        height: '20px',
        backgroundColor: `rgb(${squareColor[0]}, ${squareColor[1]}, ${squareColor[2]})`,
      }}
      onMouseEnter={handleMouseEnter}
    >
    </div>
  );
};

export default Square;
