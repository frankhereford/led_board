import React, { useEffect, useState } from 'react';

import { useContext } from 'react';
import { AppContext } from '~/pages/contexts/AppContext';

import { api } from "~/utils/api";

interface SquareProps {
  x: number;
  y: number;
  color: number[];
}

const Square: React.FC<SquareProps> = ({ x, y, color }) => {
  const setColor = api.square.setColor.useMutation({});
  //const getColor = api.square.getColor.useQuery({x: x, y: y});
  const [squareColor, setSquareColor] = useState<number[]>([0,0,0]);
  const { colorArrays, isMouseDown, activeSwatch } = useContext(AppContext);

  useEffect(() => {
    setSquareColor(color);
  }, [color]);

  const handleMouseEnter = () => {
    if (isMouseDown) {
      setColor.mutate({ x: x, y: y, color: colorArrays[activeSwatch]! })
    }
  };

  const handleMouseDown = () => {
    setColor.mutate({ x: x, y: y, color: colorArrays[activeSwatch]! })
  };

  return (
    <div
      style={{
        width: '20px',
        height: '20px',
        backgroundColor: `rgb(${squareColor[0]}, ${squareColor[1]}, ${squareColor[2]})`,
      }}
      onMouseEnter={handleMouseEnter}
      onMouseDown={handleMouseDown}
    >
    </div>
  );
};

export default Square;
