import axios from "axios";
import { Answer, AnswerWithoutDetail, ChatInfo } from "./types";

// もう使わない
// type testBackEndServerInput = {
//   prompt: string;
// };
// type testBackEndServerOutput = string;
// export const testBackEndServer = (
//   json: testBackEndServerInput
// ): Promise<testBackEndServerOutput> => {
//   return axios
//     .post("http://127.0.0.1:5000/chat", json, {
//       headers: {
//         "Content-Type": "application/json",
//       },
//     })
//     .then((res) => {
//       return res.data;
//     });
// };

type getAnswerInput = {
  prompt: string;
  chat_id: number;
  user_id: number;
};
type getAnswerOutput = Answer;
export const getAnswer = (json: getAnswerInput): Promise<getAnswerOutput> => {
  return axios
    .post("http://127.0.0.1:5000/chat", json, {
      headers: {
        "Content-Type": "application/json",
      },
    })
    .then((res) => {
      return res.data;
    })
    .then((data) => {
      // 文字列かAnsoerオブジェクトか
      // 文字列の場合は無理やりオブジェクトに変換
      if (data.isJson) {
        console.assert("recommends" in data.answer);
        console.assert(data.answer.recommends);
        return data.answer;
      } else {
        return { recommends: [{ reason: data.answer, products: [] }] };
      }
    });
};

type getQAHistoryInput = {
  user_id: number;
  chat_id: number;
};
type getQAHistoryOutput = { question: string; answer: Answer }[];
export const getQAHistory = (
  json: getQAHistoryInput
): Promise<getQAHistoryOutput> => {
  return axios
    .post("http://127.0.0.1:5000/qa_history", json, {
      headers: {
        "Content-Type": "application/json",
      },
    })
    .then((res) => {
      return res.data;
    });
};

type getChatInfosInput = {
  user_id: number;
};
type getChatInfosOutput = ChatInfo[];
export const getChatInfos = (
  json: getChatInfosInput
): Promise<getChatInfosOutput> => {
  return axios
    .post("http://127.0.0.1:5000/chat_infos", json, {
      headers: {
        "Content-Type": "application/json",
      },
    })
    .then((res) => {
      return res.data;
    });
};

type getIsValidUserInput = {
  user_id: number;
  password: string;
};
type getIsValidUserOutput = { name?: string };
export const getIsValidUser = (
  json: getIsValidUserInput
): Promise<getIsValidUserOutput> => {
  return axios
    .post("http://127.0.0.1:5000/is_valid_user", json, {
      headers: {
        "Content-Type": "application/json",
      },
    })
    .then((res) => {
      return res.data;
    });
};

type getNewChatInput = { user_id: number };
type getNewChatOutput = { chat_id: number };
export const getNewChat = (
  json: getNewChatInput
): Promise<getNewChatOutput> => {
  return axios
    .post("http://127.0.0.1:5000/new_chat", json, {
      headers: {
        "Content-Type": "application/json",
      },
    })
    .then((res) => {
      return res.data;
    });
};

type updateChatTitleInput = { chat_id: number; title: string };
type updateChatTitleOutput = { chat_id: number; title: string };
export const updateChatTitle = (
  json: updateChatTitleInput
): Promise<updateChatTitleOutput> => {
  return axios
    .post("http://127.0.0.1:5000/update_chat_title", json, {
      headers: {
        "Content-Type": "application/json",
      },
    })
    .then((res) => {
      return res.data;
    });
};

type addQAHistoryInput = {
  chat_id: number;
  user_id: number;
  question: string;
  answer: AnswerWithoutDetail;
};
type addQAHistoryOutput = { chat_id: number };
export const addQAHistory = (
  json: addQAHistoryInput
): Promise<addQAHistoryOutput> => {
  return axios
    .post("http://127.0.0.1:5000/add_qa_history", json, {
      headers: {
        "Content-Type": "application/json",
      },
    })
    .then((res) => {
      return res.data;
    });
};
