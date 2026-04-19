"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export type DeviationFlag = {
  nerve_key?: string;
  parameter?: string;
  value?: number;
  limit?: number;
  limit_type?: string;
  direction?: string;
};

function formatDeviation(d: DeviationFlag, index: number) {
  const nerve = d.nerve_key ?? "?";
  const param = d.parameter ?? "?";
  const dir = d.direction === "above" ? "powyżej normy" : d.direction === "below" ? "poniżej normy" : (d.direction ?? "");
  const val = d.value != null ? String(d.value) : "?";
  const lim = d.limit != null ? String(d.limit) : "?";
  return `${index + 1}. ${nerve} — ${param}: ${val} (${dir}, granica ${lim})`;
}

type Props = {
  value: string;
  onChange: (next: string) => void;
  deviations: DeviationFlag[];
};

export function DescriptionEditor({ value, onChange, deviations }: Props) {
  return (
    <Card className="flex h-full min-h-0 flex-col">
      <CardHeader>
        <CardTitle>DescriptionEditor</CardTitle>
        <CardDescription>Szkic opisu wygenerowany przez model AI — zweryfikuj treść przed zatwierdzeniem.</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-4 overflow-auto">
        {deviations.length > 0 ? (
          <div className="rounded-xl border border-border bg-muted/40 px-4 py-3 text-sm leading-relaxed text-foreground">
            <p className="font-medium text-foreground">Flagi od norm</p>
            <ul className="mt-2 space-y-1 pl-4">
              {deviations.map((d, i) => (
                <li key={i} className="list-disc">
                  {formatDeviation(d, i)}
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">Brak przekroczeń względem zadanych progów.</p>
        )}
        <div className="grid min-h-0 flex-1 gap-2">
          <Label htmlFor="emg-draft">Treść opisu</Label>
          <Textarea
            id="emg-draft"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="min-h-[280px] flex-1 resize-y font-mono text-sm leading-relaxed"
            placeholder="Po wygenerowaniu analizy pojawi się tu szkic opisu..."
          />
        </div>
      </CardContent>
    </Card>
  );
}
