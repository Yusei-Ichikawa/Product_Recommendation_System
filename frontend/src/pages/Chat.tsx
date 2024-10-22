import React, { useEffect, useReducer, useRef, useState } from "react";
import { FormEventHandler } from "react";
import {
  Chat as Chat_,
  ChatAction,
  initialChat,
  Message,
  AnswerMessage,
  QuestionMessage,
  ChatInfo,
  AnswerWithoutDetail,
  answerRemovedDetail,
} from "../types";
import AnswerBlock from "../Components/AnswerBlock";
import Text from "../Components/Text";
import {
  addQAHistory,
  getAnswer,
  getChatInfos,
  getNewChat,
  getQAHistory,
  updateChatTitle,
} from "../apis";
import Spinner from "../Components/Spinner";
import { Link, useNavigate, useParams } from "react-router-dom";
import { RiSendPlane2Fill } from "react-icons/ri";
import { TbPencilPlus } from "react-icons/tb";
import { RxCross2 } from "react-icons/rx";
import recopi from "../recopi_croppped.png";

const Recopi = () => (
  <div className="w-16 h-16">
    <img src={recopi} className="p-1 rounded-full" alt="レコピの画像" />
  </div>
);

const ChatBlock = ({
  chat,
  sending,
  readingHistory,
  refChatBottom,
}: {
  chat: Chat_;
  sending: boolean;
  readingHistory: boolean;
  refChatBottom: React.RefObject<HTMLDivElement>;
}) => {
  return (
    <div className="px-5">
      <ul>
        {/* 過去の履歴を読み込み中の場合 */}
        {readingHistory && (
          <li key={0} className="mt-10 flex justify-end">
            <div className="max-w-[40rem] min-w-24 bg-[#2a231f07]  p-4 text-xl rounded-2xl text-white">
              <Spinner text={"履歴を読み込み中"} isWhite />
            </div>
          </li>
        )}
        {/* チャットがまだない場合 */}
        {!readingHistory && !readingHistory && chat.messages.length === 0 && (
          <li key={0} className="mt-10 flex justify-start">
            <Recopi />
            <div className="max-w-[40rem] min-w-24 bg-[#2A231F] p-4 text-xl rounded-2xl text-white">
              レコピに何でも聞いてね！
            </div>
          </li>
        )}
        {/* チャットが1つ以上ある場合 */}
        {!readingHistory &&
          chat.messages.map((mes) => {
            console.log(chat.messages);
            if (mes.type === "question") {
              const qMes = mes as QuestionMessage;
              // 質問の場合
              return (
                <li key={qMes.id * 2} className="mt-10 flex justify-end mr-16">
                  <div className="max-w-[40rem] min-w-24 bg-[#2A231F] p-4 text-xl rounded-2xl text-white">
                    <Text>{qMes.text}</Text>
                  </div>
                </li>
              );
            } else if (mes.type === "answer") {
              const aMes = mes as AnswerMessage;
              // 解答の場合
              return (
                <li key={aMes.id * 2 + 1} className="flex justify-start mt-10 ">
                  <Recopi />
                  <div className="grow bg-[#2A231F] max-w-[50rem] min-w-24 p-4 rounded-2xl text-white">
                    <AnswerBlock answer={aMes.answer} />
                  </div>
                </li>
              );
            }
          })}
        {/* 答えが返ってくるのを待っている場合 */}
        {sending && (
          <li className="mt-10 flex justify-start">
            <Recopi />
            <div className="bg-[#2A231F] max-w-[50rem] min-w-24 p-4 rounded-2xl text-white">
              <Spinner text={"処理中"} isWhite />
            </div>
          </li>
        )}
      </ul>
      {/* スクロール用 */}
      <div ref={refChatBottom} className="mt-10"></div>
    </div>
  );
};

const InputBlock = ({
  chatDispatch,
  setSending,
  setChatsInfoList,
  sending,
  chat_id,
  user_id,
}: {
  chatDispatch: React.Dispatch<ChatAction>;
  setSending: React.Dispatch<React.SetStateAction<boolean>>;
  setChatsInfoList: React.Dispatch<React.SetStateAction<ChatInfo[]>>;
  sending: boolean;
  chat_id: number;
  user_id: number;
}) => {
  const [question, setQuestion] = useState("");
  const navigate = useNavigate();
  const [areaSize, setAreaSize] = useState<number>(1);
  const onChangeHandler = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setQuestion(value);
    const splitted = value.split("\n");
    const n = splitted
      .map((s) => ((s.length / 70) | 0) + 1)
      .reduce(function (sum, element) {
        return sum + element;
      }, 0);
    setAreaSize(n);
  };
  const handleSubmit: FormEventHandler<HTMLFormElement> = (event) => {
    setSending(true);
    setQuestion("");
    event.preventDefault();
    // 質問を記録
    const form = new FormData(event.currentTarget);
    const question = (form.get("question") as string) || "";
    chatDispatch({
      type: "add",
      newMessage: { text: question, type: "question" },
    });

    // 質問をバックエンドに送信
    getAnswer({ prompt: question, chat_id, user_id })
      .then((answer) => {
        setSending(false);
        chatDispatch({
          type: "add",
          newMessage: { text: "", type: "answer", answer: answer },
        });
        // 新しいチャットを作成
        if (chat_id == -1) {
          getNewChat({ user_id })
            .then(({ chat_id: new_chat_id }) => {
              const new_chat_title = question.slice(0, 10);
              const new_chat_info: ChatInfo = {
                title: new_chat_title,
                chat_id: new_chat_id,
              };
              addQAHistory({
                chat_id: new_chat_id,
                user_id,
                question,
                answer: answerRemovedDetail(answer),
              });
              setChatsInfoList((old) => [...old, new_chat_info]);
              updateChatTitle({ chat_id: new_chat_id, title: new_chat_title });
              navigate(`/chat/${new_chat_id}`);
            })
            .catch((e) => {
              setSending(false);
              console.log("getNewChatでエラー" + e);
            });
        } else {
          addQAHistory({
            chat_id,
            user_id,
            question,
            answer: answerRemovedDetail(answer),
          });
        }
      })
      .catch((e) => {
        setSending(false);
        console.log("getAnswerでエラー" + e);
      });
  };
  return (
    <div className="full">
      <form onSubmit={handleSubmit} className={`flex pt-3 pl-8 justify-start`}>
        {/* 入力欄 */}
        <label className={`block grow pr-5`}>
          <textarea
            name="question"
            defaultValue=""
            value={question}
            rows={Math.min(areaSize, 3)}
            onChange={(e) => onChangeHandler(e)}
            className={`py-2 px-6 outline-none w-full ${areaSize > 3 ? "text-xs" : areaSize > 2 ? "text-sm" : "text-lg"} border border-gray-300 rounded-full`}
            title="質問を送信"
            placeholder="みつもりレコピにメッセージを送信する"
          />
        </label>
        {/* 送信ボタン */}
        <button
          type="submit"
          disabled={sending}
          className=" bg-[#4d6160] text-white px-4 rounded-lg hover:bg-[#334846] transition-colors disabled:bg-[#334846] mr-10 w-20 flex-shrink-0 h-12"
          title="質問を送信"
        >
          <div className="flex justify-between w-14 items-center">
            送信
            <RiSendPlane2Fill size={"20px"} />
          </div>
        </button>
      </form>
    </div>
  );
};

const SideNav = ({
  current_chat_id,
  setReadingChatsList,
  setChatsInfoList,
  readingChatsList,
  chatsInfoList,
  user_id,
}: {
  current_chat_id: number;
  setReadingChatsList: React.Dispatch<React.SetStateAction<boolean>>;
  setChatsInfoList: React.Dispatch<React.SetStateAction<ChatInfo[]>>;
  readingChatsList: boolean;
  chatsInfoList: ChatInfo[];
  user_id: number;
}) => {
  useEffect(() => {
    setReadingChatsList(true);
    getChatInfos({ user_id: user_id })
      .then((chatInfos: ChatInfo[]) => {
        setChatsInfoList(chatInfos);
        setReadingChatsList(false);
      })
      .catch((e) => {
        console.log("getChatInfosでエラー" + e);
        setReadingChatsList(false);
      });
  }, []);
  console.log(current_chat_id);
  return (
    <nav className="">
      {readingChatsList && (
        <Spinner text={"チャット一覧を読み込み中"} isWhite />
      )}
      <ul>
        {chatsInfoList
          .sort((a, b) => a.chat_id - b.chat_id)
          .map((chatInfo: ChatInfo) => {
            const chatTitle = chatInfo.title;
            const displayedChatTitle =
              chatTitle !== null && chatTitle.length >= 10
                ? chatTitle.slice(0, 10) + "..."
                : chatTitle === ""
                  ? "[空欄]"
                  : chatTitle;
            return (
              <li
                key={chatInfo.chat_id}
                className={`hover:bg-white hover:bg-opacity-20 rounded-md px-3 h-8 hover:text-blue-400 hover:cursor-pointer${chatInfo.chat_id === current_chat_id ? "text-red-400 hover:bg-inherit hover:decoration-inherit hover:text-inherit pointer-events-none cursor-pointer bg-white bg-opacity-20" : ""}`}
              >
                <Link to={`/chat/${chatInfo.chat_id}`}>
                  <div
                    className={`text-white w-full ${chatInfo.chat_id === current_chat_id ? "font-semibold" : ""}`}
                  >
                    {chatInfo.chat_id}:{displayedChatTitle}
                  </div>
                </Link>
              </li>
            );
          })}
      </ul>
    </nav>
  );
};

const CreateNewChat = ({
  user_id,
  setChatsInfoList,
  setCreating,
}: {
  user_id: number;
  setChatsInfoList: React.Dispatch<React.SetStateAction<ChatInfo[]>>;
  setCreating: React.Dispatch<React.SetStateAction<boolean>>;
}) => {
  const navigate = useNavigate();
  const createNewChat = () => {
    setCreating(true);
    getNewChat({ user_id })
      .then((ans) => {
        const new_chat_id = ans.chat_id;
        const new_chat_info: ChatInfo = { title: "", chat_id: new_chat_id };
        setChatsInfoList((old) => [...old, new_chat_info]);
        setCreating(false);
        navigate(`/chat/${new_chat_id}`);
      })
      .catch((e) => {
        setCreating(false);
        console.log("getNewChatでエラー" + e);
      });
  };
  return (
    <div className="hover:bg-white hover:bg-opacity-20 w-10 h-10 rounded-md">
      <button onClick={createNewChat} title="新規チャットを作成">
        <TbPencilPlus size={"32px"} color={"white"} />
      </button>
    </div>
  );
};

const Chat = ({
  user_id,
  setUserId,
}: {
  user_id: number;
  setUserId: React.Dispatch<React.SetStateAction<number>>;
}) => {
  const [creating, setCreating] = useState(false);
  const [sending, setSending] = useState(false);
  const [readingHistory, setReadingHistory] = useState(false);
  const [chatsInfoList, setChatsInfoList] = useState<ChatInfo[]>([]);
  const [readingChatsList, setReadingChatsList] = useState(false);
  // ページが変わったら過去の履歴を読み込む。
  // TODO もしダメだったら、一時的にchat_id=1を表示する
  const chat_id = Number(useParams().chatId) || -1;
  useEffect(() => {
    console.log("chat_id is changed to ", chat_id);
    if (chat_id != -1) {
      setReadingHistory(true);
      getQAHistory({ user_id: user_id, chat_id: chat_id })
        .then((qa_history) => {
          chatDispatch({
            type: "reset-and-add",
            newMessages: qa_history,
          });
          setReadingHistory(false);
          const old_title = chatsInfoList.filter(
            (chatInfo) => chatInfo.chat_id === chat_id
          )[0].title;
          console.log("old_title is ", old_title);
          if (old_title === null || old_title === "タイトル無し") {
            const new_title =
              qa_history.length > 0 &&
              qa_history[0].question !== null &&
              qa_history[0].question !== ""
                ? qa_history[0].question
                : "タイトル無し";
            updateChatTitle({ chat_id, title: new_title })
              .then(() => {
                setChatsInfoList((old) =>
                  old.map((oldChatInfo) => {
                    if (oldChatInfo.chat_id === chat_id) {
                      oldChatInfo.title = new_title;
                      return oldChatInfo;
                    } else {
                      return oldChatInfo;
                    }
                  })
                );
              })
              .catch((e) => {
                setReadingHistory(false);
                console.log("updateChatTitleでエラー" + e);
              });
          }
        })
        .catch((e) => {
          setReadingHistory(false);
          console.log("getQAHistoryでエラー" + e);
        });
    }
  }, [chat_id]);
  // スクロール
  const refChatBottom = useRef<HTMLDivElement>(null);
  useEffect(() => {
    refChatBottom.current!.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [sending, readingHistory]);
  // Chatの管理
  const chatReducer = (chat: Chat_, action: ChatAction) => {
    switch (action.type) {
      case "add": {
        const newMessage: Message = { ...action.newMessage!, id: chat.id };
        const newChat: Chat_ = {
          messages: [...chat.messages, newMessage],
          id: chat.id + 1,
        };
        return newChat;
      }
      case "reset-and-add": {
        const newChat: Chat_ = {
          messages: [],
          id: 0,
        };
        action.newMessages?.forEach((qa, idx) => {
          const newQ: QuestionMessage = {
            text: qa.question,
            type: "question",
            id: idx,
          };
          const newA: AnswerMessage = {
            text: "",
            type: "answer",
            id: idx,
            answer: qa.answer,
          };
          newChat.messages = [...newChat.messages, newQ, newA];
        });
        newChat.id = action.newMessages!.length;
        return newChat;
      }
    }
  };
  const [chat, chatDispatch] = useReducer(chatReducer, initialChat);
  const clearClipboard = async () => {
    await global.navigator.clipboard.writeText("");
  };
  const [errorMessage, setErrorMessage] = useState("");
  return (
    <div className="h-svh w-svw">
      {/* エラーの表示 */}
      {errorMessage !== "" && (
        <div className="w-96 min-h-16 absolute top-10 right-10 z-10 rounded-xl border-2 bg-gray-100 border-gray-50 bg-opacity-90">
          <div className=" text-red-500 p-2 text-lg">{errorMessage}</div>
          <button
            className="rounded-full h-5 w-5 border-[1px] border-black leading-3 flex items-center absolute -top-2 -left-2"
            title="エラー表示を消す"
            onClick={() => {
              setErrorMessage("");
            }}
          >
            <RxCross2 size={"20px"} />
          </button>
        </div>
      )}
      <div className=" h-svh w-svw flex">
        <div className="w-64 bg-[#211a16] flex flex-col">
          {/* チャットの作成 */}
          <div className="h-20 flex-shrink-0 pt-5 flex justify-end mr-5">
            <CreateNewChat
              user_id={user_id}
              setChatsInfoList={setChatsInfoList}
              setCreating={setCreating}
            />
          </div>
          <div className="overflow-auto grow">
            <SideNav
              current_chat_id={chat_id}
              setReadingChatsList={setReadingChatsList}
              setChatsInfoList={setChatsInfoList}
              chatsInfoList={chatsInfoList}
              readingChatsList={readingChatsList}
              user_id={user_id}
            />
            <div>
              {creating && <Spinner text="新規チャットを作成中" isWhite />}
            </div>
          </div>
        </div>
        <div className="grow flex flex-col h-full bg-[#292522]">
          {/* 上の入力欄とログアウトボタンとか */}
          <div className="h-12 flex-shrink-0">
            <div className="flex justify-end pr-20 pt-3">
              <button
                onClick={clearClipboard}
                className="text-[#efd9b4] mr-5 hover:text-[#9b8867]"
                title="クリップボードをクリア"
              >
                コピーをクリア
              </button>
              <button
                className="mr-5 text-[#efd9b4] hover:text-[#9b8867]"
                onClick={() => {
                  localStorage.setItem("user_id", "-1");
                  setUserId(-1);
                }}
                title="ログアウト"
              >
                ログアウト
              </button>
              <div className="text-[#efd9b4] ml-5">user_id: {user_id}</div>
            </div>
          </div>
          <div className=" overflow-auto grow">
            <ChatBlock
              chat={chat}
              sending={sending}
              readingHistory={readingHistory}
              refChatBottom={refChatBottom}
            />
          </div>
          <div className="h-24 flex-shrink-0 ">
            {/* 質問入力 */}
            <InputBlock
              chatDispatch={chatDispatch}
              setSending={setSending}
              setChatsInfoList={setChatsInfoList}
              sending={sending}
              chat_id={chat_id}
              user_id={user_id}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
