import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getIsValidUser } from "../apis";
import Spinner from "../Components/Spinner";

const Login = ({
  setUserIdGlob,
}: {
  setUserIdGlob: React.Dispatch<React.SetStateAction<number>>;
}) => {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isFailed, setIsFailed] = useState(false);
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    getIsValidUser({ user_id: Number(userId), password: password })
      .then((user) => {
        const name = user.name;
        setIsLoading(false);
        if (name != null) {
          console.log("login success");
          localStorage.setItem("user_id", userId);
          console.log(userId, localStorage.getItem("user_id"));
          setUserIdGlob(Number(userId));
          navigate("/chat");
        } else {
          setIsFailed(true);
          setUserId("");
          setPassword("");
        }
      })
      .catch((e) => {
        setIsFailed(true);
        setUserId("");
        setPassword("");
        console.log("getIsValidUserでエラー" + e);
      });
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-sm">
        <h2 className="text-2xl font-semibold text-center text-gray-800">
          Login
        </h2>
        <form onSubmit={handleLogin} className="mt-8">
          <div className="mb-4">
            <label
              className="block text-gray-700 text-sm font-bold mb-2"
              htmlFor="userId"
            >
              User ID
            </label>
            <input
              id="userId"
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="Enter your user ID"
            />
          </div>
          <div className="mb-6">
            <label
              className="block text-gray-700 text-sm font-bold mb-2"
              htmlFor="password"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="Enter your password"
            />
          </div>
          <div className="h-10">
            {isLoading && (
              <div>
                <Spinner text="認証中" />
              </div>
            )}
            {!isLoading && isFailed && (
              <p className="text-red-500 italic h-10">認証に失敗しました</p>
            )}
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
