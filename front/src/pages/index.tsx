// frontend/src/pages/index.tsx
import React, { useState } from "react";
import { Button, Textarea, TextInput, Container, Title } from "@mantine/core";
import axios from "axios";
 import PlayerWrapper from "../remotion/MyComposition";

export default function Home(){
  const [prompt,setPrompt] = useState("");
  const [script,setScript] = useState("");
  const [assets,setAssets] = useState<any>(null);
  const [audioUrl,setAudioUrl] = useState("");

  const generate = async ()=>{
    try{
      const res = await axios.post("http://localhost:8000/generate", { prompt, length: 30 });
      setScript(res.data.script);
      setAssets({ images: res.data.images, videos: res.data.videos });
      setAudioUrl(`http://localhost:8000${res.data.audio}`);
    }catch(e){
      alert("Generate failed. Check backend.");
      console.error(e);
    }
  };

  const exportVideo = async ()=>{
    try{
      const res = await axios.post("http://localhost:8000/export", {
        images: assets.images,
        videos: assets.videos,
        audio: audioUrl
      });
      const url = `http://localhost:8000${res.data.download_url}`;
      window.open(url, "_blank");
    }catch(e){
      alert("Export failed.");
      console.error(e);
    }
  };

  return (
    <Container>
      <Title order={3} mb="md">Duber</Title>
      <TextInput placeholder="Prompt (what to make the short about)" value={prompt} onChange={(e)=>setPrompt(e.currentTarget.value)} />
      <Textarea placeholder="Generated script" mt="sm" value={script} onChange={(e)=>setScript(e.currentTarget.value)} />
      <Button mt="sm" onClick={generate}>Generate</Button>

      {assets && (
        <>
          <PlayerWrapper assets={assets} audioUrl={audioUrl} script={script} />
          <Button mt="md" onClick={exportVideo}>Export (mp4)</Button>
        </>
      )}
    </Container>
  );
}
