import React from "react";

const Text = ({
  className = "",
  children,
}: {
  className?: string;
  children: string;
}) => {
  return <p className={` ${className}`}>{children}</p>;
};

export default Text;
