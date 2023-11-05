import React, { useEffect, useState } from 'react';

import { api } from "~/utils/api";

interface SquareProps {
  x: number;
  y: number;
}

const Square: React.FC<SquareProps> = ({ x, y }) => {
  const setColor = api.square.color.useMutation({});
  const [squareColor, setSquareColor] = useState<number[]>([0,0,0]);

  useEffect(() => {
    setColor.mutate({ x: x, y: y, color: squareColor })
  }, [squareColor]);

  //const handleMouseEnter = () => {
    //if (isMouseDown.value) {
      //setSquareColor(inks.value[0]!);
    //}
  //};

  return (
    <div
      style={{
        width: '20px',
        height: '20px',
        backgroundColor: `rgb(${squareColor[0]}, ${squareColor[1]}, ${squareColor[2]})`,
      }}
      //onMouseEnter={handleMouseEnter}
    >
    </div>
  );
};

export default Square;
