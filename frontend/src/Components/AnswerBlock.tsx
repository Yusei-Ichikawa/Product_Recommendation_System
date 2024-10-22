import React, { useState } from "react";
import { Answer, ARecommend, Product } from "../types";
import { FaExternalLinkAlt } from "react-icons/fa";
import { BsCopy } from "react-icons/bs";
import { RxCross2 } from "react-icons/rx";

const ProductBlock = ({ product }: { product: Product }) => {
  const [errorMessage, setErrorMessage] = useState("");
  const copyText = async () => {
    global.navigator.clipboard
      .readText()
      .then((beforeClipBoard) => {
        if (beforeClipBoard === "") {
          global.navigator.clipboard.writeText(product.id);
        } else {
          global.navigator.clipboard.writeText(
            beforeClipBoard + "\n" + product.id
          );
        }
      })
      .catch((e) => {
        console.log("クリップボードの読み込みでエラー" + e);
        setErrorMessage(
          "コピー後に出てく「ペースト」を押してください。(Chromeの場合はクリップボードへのアクセスを許可してください。)"
        );
      });
  };
  return (
    <div className="flex items-center hover:bg-white hover:bg-opacity-10 p-2 rounded-lg">
      {/* エラー表示 */}
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
      <div className="w-48 flex space-between mr-5 items-center hover:underline">
        <button
          onClick={copyText}
          className="border-2 rounded-xl h-10 w-28 text-lg bg-white bg-opacity-5 hover:bg-opacity-10 active:bg-opacity-20 flex items-center mr-5"
        >
          <div className="p-2 no-underline">コピー</div> <BsCopy />
        </button>
        <div className="text-xl mr-3 w-20">{product.id}</div>
      </div>
      <div className="w-40 text-xl">{product.name}</div>
      <div className="w-36 text-xl">{product.price}円</div>
      <img
        src={`data:image/jpeg;base64,${product.imageEncoding}`}
        alt={product.name}
        className="h-16 w-16 mr-5"
      />
      <div className="w-12 h-12 flex items-center justify-center">
        <a
          // href={product.url}
          href="https://www.otsuka-shokai.co.jp/products/mfp-copy-printer/hard/category/mono/"
          target="_blank"
          rel="noreferrer noopener"
          className="text-blue-300 hover:text-blue-500 block h-6 w-6 hover:h-8 hover:w-8"
          title={product.id + "(" + product.name + ")" + "の詳細サイト"}
        >
          <FaExternalLinkAlt color={"white"} size={"100%"} />
        </a>
      </div>
    </div>
  );
};

const RecommendBlock = ({ aRecommend }: { aRecommend: ARecommend }) => {
  return (
    <div>
      <div className="border-b-4">
        {/* recomends */}
        <ol>
          {aRecommend.products.map((product, idx) => (
            <li key={idx} className="mt-6 mb-2">
              <ProductBlock product={product} />
            </li>
          ))}
        </ol>
      </div>
      <div className="text-xl ml-10 p-4 bg-opacity-10 mt-2 leading-8">
        {aRecommend.reason}
      </div>
    </div>
  );
};

const AnswerBlock = ({ answer }: { answer: Answer }) => {
  console.log(answer);
  return (
    <div>
      <div>
        {/* recomends */}
        {answer.recommends !== undefined && answer.recommends.length > 0 ? (
          <ul>
            {answer.recommends.map((recommend, idx) => (
              <li key={idx}>
                <RecommendBlock aRecommend={recommend} />
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-xl">一致するものが見つかりませんでした。</div>
        )}
        {/* <ul>
          {answer.recommends.map((recommend, idx) => (
            <li key={idx}>
              <RecommendBlock aRecommend={recommend} />
            </li>
          ))}
        </ul> */}
      </div>
    </div>
  );
};

export default AnswerBlock;
