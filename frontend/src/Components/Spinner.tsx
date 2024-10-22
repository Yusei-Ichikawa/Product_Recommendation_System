import React from "react";
import { AiOutlineLoading3Quarters } from "react-icons/ai";

const Spinner = ({
  text,
  isWhite = false,
}: {
  text: string;
  isWhite?: boolean;
}) => {
  return (
    <div className="flex">
      <div className={`justify-center w-10 h-10 animate-spin`}>
        <AiOutlineLoading3Quarters
          size={"40px"}
          color={isWhite ? "white" : "black"}
        />
      </div>
      <div className={`${isWhite ? "text-white" : "text-black"} text-2xl`}>
        {text}
      </div>
    </div>
  );
};

export default Spinner;
