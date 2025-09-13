// // frontend/src/remotion/MyComposition.tsx
// import React from "react";

// export default function MyComposition({ assets, audioUrl, script }: any) {
//   const visual = (assets?.videos?.[0] || assets?.images?.[0]) || "";
//   const lines = (script || "").split("\n").slice(0,3);

//   return (
//     <div style={{ width: 960, height: 540, background: "#111", position: "relative" }}>
//       {visual ? <img src={visual} style={{ width: "100%", height: "100%", objectFit: "cover" }} /> : <div style={{color:'white'}}>No visual</div>}
//       <div style={{ position: "absolute", left: 40, bottom: 40, color: "white" }}>
//         {lines.map((l:string,i:number)=> <div key={i} style={{ fontSize: 36, fontWeight:700, textShadow: '0 2px 8px rgba(0,0,0,0.7)' }}>{l}</div>)}
//       </div>
//       {audioUrl && <audio src={audioUrl} controls style={{ position: "absolute", top: 8, left: 8 }} />}
//     </div>
//   );
// }


import React, { useState, useEffect } from "react";
import { Text, Paper } from "@mantine/core";

interface MyCompositionProps {
  assets: {
    images: string[];
    videos: string[];
  };
  script: string;
  audioUrl: string;
}

const MyComposition: React.FC<MyCompositionProps> = ({ assets, script, audioUrl }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  // Cycle through images/videos every 2 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % Math.max(assets.videos.length, assets.images.length));
    }, 2000);
    return () => clearInterval(interval);
  }, [assets]);

  const visual = assets.videos[currentIndex] || assets.images[currentIndex] || "";

  return (
    <Paper p="md" shadow="xs" style={{ textAlign: "center" }}>
      <Text size="lg" weight={500} mb="sm">
        Generated Script
      </Text>
      <Text size="md" mb="md" color="dimmed">
        {script}
      </Text>

      {visual.endsWith(".mp4") ? (
        <video src={visual} controls width="100%" />
      ) : (
        <img src={visual} alt="Preview" width="100%" />
      )}

      {audioUrl && (
        <audio controls style={{ marginTop: "1rem" }}>
          <source src={audioUrl} type="audio/mpeg" />
          Your browser does not support the audio element.
        </audio>
      )}
    </Paper>
  );
};

export default MyComposition;
