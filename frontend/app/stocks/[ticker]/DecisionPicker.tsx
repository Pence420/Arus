"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import "./decision.css";

export default function DecisionPicker({ ticker }: { ticker: string }) {
  const [value, setValue] = useState("");
  const router = useRouter();
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!value) return;
    router.push(`/stocks/${ticker}?decision_at=${encodeURIComponent(`${value}:00+07:00`)}`);
  }
  return <form className="decision-form" onSubmit={submit}>
    <label htmlFor="decision-at">Ubah jam keputusan (WIB)</label>
    <div><input id="decision-at" type="datetime-local" value={value} onChange={(event) => setValue(event.target.value)} required /><button type="submit">Terapkan</button></div>
  </form>;
}
