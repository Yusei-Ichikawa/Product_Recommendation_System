export type Chat = {
  messages: Message[];
  id: number;
};
export const initialChat: Chat = { messages: [], id: 0 };

export type ChatAction = {
  type: "add" | "reset-and-add";
  newMessage?: Omit<QuestionMessage, "id"> | Omit<AnswerMessage, "id">;
  newMessages?: { question: string; answer: Answer }[];
};

export type QuestionMessage = {
  text: string;
  type: "question" | "answer";
  id: number;
};

export type AnswerMessage = {
  text: string;
  type: "question" | "answer";
  id: number;
  answer: Answer;
};

export type Message = QuestionMessage | AnswerMessage;

export type Product = {
  id: string;
  name: string;
  price: string;
  url: string;
  imageEncoding: string;
};

export type ARecommend = {
  reason: string;
  products: Product[];
};

export type Answer = {
  recommends: ARecommend[];
};

// 商品ID、理由のみ
export type AnswerWithoutDetail = {
  recommends: { ids: string[]; reason: string }[];
};

export const answerRemovedDetail = (answer: Answer): AnswerWithoutDetail => {
  return {
    recommends: answer.recommends.map((recommend) => {
      return {
        reason: recommend.reason,
        ids: recommend.products.map((product) => product.id),
      };
    }),
  };
};

export type ChatInfo = {
  title: string;
  chat_id: number;
};

// example
const printerImageEncodingExsample =
  "data:image/jpeg;base64,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";
const printerExsamples: Product[] = [
  {
    id: "HUCO1",
    name: "Canon PIXUS TS8330",
    price: "20,000円",
    url: "https://cweb.canon.jp/pixus/lineup/allinone/ts8330.html",
    imageEncoding: printerImageEncodingExsample,
  },
  {
    id: "HUCO2",
    name: "Epson Colorio EP-879AW",
    price: "18,000円",
    url: "https://www.epson.jp/products/colorio/ep879aw/",
    imageEncoding: printerImageEncodingExsample,
  },
  {
    id: "HUCO3",
    name: "Brother PRIVIO DCP-J982N",
    price: "15,000円",
    url: "https://www.brother.co.jp/product/printer/inkjet/dcpj982n/index.htm",
    imageEncoding: printerImageEncodingExsample,
  },
  {
    id: "HUCO4",
    name: "HP ENVY 4520",
    price: "12,000円",
    url: "https://support.hp.com/jp-ja/product/hp-envy-4520-all-in-one-printer-series/5447920",
    imageEncoding: printerImageEncodingExsample,
  },
  {
    id: "HUCO5",
    name: "Canon PIXMA G6030",
    price: "22,000円",
    url: "https://cweb.canon.jp/pixma/lineup/g6030.html",
    imageEncoding: printerImageEncodingExsample,
  },

  {
    id: "HUCO6",
    name: "Epson EcoTank ET-2760",
    price: "25,000円",
    url: "https://www.epson.jp/products/ecotank/et2760/",
    imageEncoding: printerImageEncodingExsample,
  },
  {
    id: "HUCO7",
    name: "Brother MFC-J995DW",
    price: "20,500円",
    url: "https://www.brother.co.jp/product/printer/inkjet/mfcj995dw/index.htm",
    imageEncoding: printerImageEncodingExsample,
  },
  {
    id: "HUCO8",
    name: "HP OfficeJet Pro 9025",
    price: "28,000円",
    url: "https://www8.hp.com/jp/ja/printers/officejet-pro.html",
    imageEncoding: printerImageEncodingExsample,
  },
  {
    id: "HUCO9",
    name: "Canon PIXUS TR9530",
    price: "19,500円",
    url: "https://cweb.canon.jp/pixus/lineup/allinone/tr9530.html",
    imageEncoding: printerImageEncodingExsample,
  },
  {
    id: "HUCO10",
    name: "Epson Colorio EP-712A",
    price: "17,000円",
    url: "https://www.epson.jp/products/colorio/ep712a/",
    imageEncoding: printerImageEncodingExsample,
  },
];
const lightImageEncodingExsample =
  "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCABAAEADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iio55PKgd+4HFAEE91tYxx9R1b0qqz5OWOT7mohkrkH8ahLc1VgLavtOVOD7VbgutzBJOp6H1rNjyx4qSTK/WiwGxRUcEnmwI/cjmpKkAqvfAmylx2Gf1qxSEBlKkZBGDQBgxyYjIqM/epLrfazvEVBA6H1FQrcFj90VQF2A4apLgg4qCJs9qtRw+dIq469T7UAXrIFbOPPcZqxSABQABgDgUtSAUUUUAZWsRjMUmPVTWRtw9dFqEQls3zwV+YGueMUm4HeDn2qkI0LZcrWjZryzfhWfbxuI8l8D6VqWybYRzknkmkwJqKKKQwooooAbIA0bA9CCK8L8XxTDwaghaS3kiunHnxBgzA5GCwGOh/SvdiMjFeOeP8ATp9Lt3tr2NP7OmmLw3aRsxB67XweD17YNICPRmk/4V9psDnzW84Bp3GZHwx6tnPt0r2SH/UR8Y+Ufyrx/wAFW0+v2dvp9nGx0+1k3TXbptX12rkZJ59cV7EqhEVVGFUYAoAWiiimB//Z";
const lightBulbsExsample: Product[] = [
  {
    id: "LB001",
    name: "Philips Hue White and Color Ambiance",
    price: "7,500円",
    url: "https://www.philips-hue.com/ja-jp/p/hue-white-and-color-ambiance-%E3%83%87%E3%83%A5%E3%82%A2%E3%83%83%E3%82%AF-e26/8718699673140",
    imageEncoding: lightImageEncodingExsample,
  },
  {
    id: "LB002",
    name: "Panasonic LED電球 60形相当",
    price: "1,000円",
    url: "https://panasonic.jp/light/products/led_lamp/lamp/index.html",
    imageEncoding: lightImageEncodingExsample,
  },
  {
    id: "LB003",
    name: "IKEA TRÅDFRI LED電球",
    price: "2,000円",
    url: "https://www.ikea.com/jp/ja/p/tradfri-led-e26-400-lm-wireless-dimmable-white-spectrum-opal-white-80357978/",
    imageEncoding: lightImageEncodingExsample,
  },
  {
    id: "LB004",
    name: "Toshiba ネオボールZ REAL 100W形",
    price: "1,800円",
    url: "https://www.tlt.co.jp/tlt/products/light-source/lamp/",
    imageEncoding: lightImageEncodingExsample,
  },
  {
    id: "LB005",
    name: "アイリスオーヤマ LED電球 昼光色 60W相当",
    price: "800円",
    url: "https://www.irisohyama.co.jp/products/led/ledlamp/",
    imageEncoding: lightImageEncodingExsample,
  },
];

export const answerExample: Answer = {
  recommends: [
    {
      reason:
        "コストパフォーマンスが高く、家庭での使用に最適な電球とプリンターのセットです。",
      products: [lightBulbsExsample[1], printerExsamples[2]],
    },
    {
      reason: "スマートホームを構築するための高機能電球と多機能プリンター。",
      products: [lightBulbsExsample[0], printerExsamples[0]],
    },
    {
      reason:
        "長期的なコスト削減を目指す方に最適なインクと電気代の節約ができるセットです。",
      products: [lightBulbsExsample[3], printerExsamples[5]],
    },
  ],
};
