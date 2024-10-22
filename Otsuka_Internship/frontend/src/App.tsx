import React, { useEffect, useState } from "react";
import { Routes, Route, BrowserRouter, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Chat from "./pages/Chat";

const App = () => {
  const [userId, setUserId] = useState<number>(-1);
  useEffect(() => {
    console.log("app useEffect");
    console.log("before", userId);
    setUserId(
      localStorage.getItem("user_id") === null ||
        localStorage.getItem("user_id")! in ["-1", "0"]
        ? -1
        : Number(localStorage.getItem("user_id"))
    );
    console.log(localStorage.getItem("user_id"));
    // const user_id = localStorage.getItem("user_id");
    // console.log("A:", user_id);
    // const name = localStorage.getItem("user_name");
    // if (user_id != "-1") {
    //   // setUserId(Number(localStorage.getItem("user_id"))!);
    //   console.log("aaaa");
    //   console.log(localStorage.getItem("user_id"));
    // }
  });
  return (
    <BrowserRouter>
      <Routes>
        {/* indexにアクセスしたら、認証されていたらchatにそうでない場合はloginに */}
        <Route
          path="/"
          element={
            userId != -1 ? <Navigate to="/chat" /> : <Navigate to="/login" />
          }
        />
        {/* ログインページ */}
        <Route
          path="/login"
          element={
            userId != -1 ? (
              <Navigate to="/chat" />
            ) : (
              <Login setUserIdGlob={setUserId} />
            )
          }
        />
        {/* chatにアクセスしたら、認証されていたらchatにそうでない場合はloginに */}
        <Route
          path="/chat"
          element={
            userId != -1 ? (
              <Chat user_id={userId} setUserId={setUserId} />
            ) : (
              <Navigate to="/login" />
            )
          }
        >
          <Route
            path=":chatId"
            element={<Chat user_id={userId} setUserId={setUserId} />}
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
