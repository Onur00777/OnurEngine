"use client";

import { useState, useMemo } from "react";
import { Chess } from "chess.js";
import dynamic from "next/dynamic";

const Chessboard = dynamic(
  () => import("react-chessboard").then((mod) => mod.Chessboard),
  { ssr: false },
);

export default function Home() {
  const [fen, setFen] = useState(
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  );
  const [isBotThinking, setIsBotThinking] = useState(false);
  const game = useMemo(() => new Chess(), []);

  async function fetchBotMove(currentFen) {
    setIsBotThinking(true);
    try {
      // TARAYICI ENGELİNİ DELEN SİHİRLİ GEÇİT: İsteği proxy köprüsü üzerinden dolandırıyoruz
      const response = await fetch(
        "https://corsproxy.io/?url=" +
          encodeURIComponent("http://127.0.0.1:8000/get_move"),
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ fen: currentFen }),
        },
      );

      const data = await response.json();

      if (data && data.move) {
        game.load(currentFen);
        game.move(data.move);
        setFen(game.fen());
      }
    } catch (error) {
      console.error("Köprü hatası, yerel ağ kontrol ediliyor...", error);

      // EĞER KÖPRÜDE GECİKME OLURSA DİREKT YEREL DENEME (Yedek Plan)
      try {
        const responseLocal = await fetch("http://localhost:8000/get_move", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ fen: currentFen }),
        });
        const dataLocal = await responseLocal.json();
        if (dataLocal && dataLocal.move) {
          game.load(currentFen);
          game.move(dataLocal.move);
          setFen(game.fen());
        }
      } catch (err) {
        console.error("Sunucuya ulaşılamadı. Python açık mı?", err);
      }
    } finally {
      setIsBotThinking(false);
    }
  }

  function onDrop(sourceSquare, targetSquare) {
    if (isBotThinking) return false;

    game.load(fen);
    if (game.turn() === "b") return false;

    try {
      const move = game.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: "q",
      });

      if (move) {
        const newFen = game.fen();
        setFen(newFen);

        if (!game.isGameOver()) {
          fetchBotMove(newFen);
        }
        return true;
      }
    } catch (e) {
      return false;
    }
    return false;
  }

  const currentTurn = fen.split(" ")[1];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-zinc-900 text-white p-4">
      <div className="w-full max-w-[500px]">
        <h1 className="text-3xl color-red font-bold text-center mb-8 text-zinc-100 drop-shadow-md select-none">
          BetaOne by Onur Yüksek
        </h1>

        <div className="shadow-2xl shadow-black/80 rounded-md overflow-hidden border-2 border-zinc-700 bg-zinc-800">
          <Chessboard
            position={fen}
            onPieceDrop={onDrop}
            boardOrientation="white"
            customDarkSquareStyle={{ backgroundColor: "#779556" }}
            customLightSquareStyle={{ backgroundColor: "#ebecd0" }}
          />
        </div>

        <div className="mt-8 text-center space-y-3">
          <div className="text-lg font-semibold bg-zinc-800 py-3 px-6 rounded-lg inline-block shadow-inner border border-zinc-700 select-none w-full max-w-[350px]">
            {isBotThinking
              ? "⚫ BetaOne Analiz Yapıyor (Derinlik: 3)..."
              : "⚪ Sıra Sende, Hamleni Yap!"}
          </div>
        </div>
      </div>
    </div>
  );
}
