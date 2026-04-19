"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import {
  DescriptionEditor,
  type DeviationFlag,
} from "@/components/DescriptionEditor";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiFetch, apiUrl, getStoredToken, setStoredToken } from "@/lib/api";

const NERVE_OPTIONS = [
  { label: "Nerw pośrodkowy", value: "nerw_pośrodkowy" },
  { label: "Nerw łokciowy", value: "nerw_łokciowy" },
  { label: "Nerw promieniowy", value: "nerw_promieniowy" },
  { label: "Nerw strzałkowy", value: "nerw_strzałkowy" },
] as const;

const DEFAULT_NORMS = `{
  "default": {
    "latency_ms_max": 4.5,
    "amplitude_mv_min": 4.0,
    "f_wave_latency_ms_max": 32,
    "conduction_velocity_m_s_min": 48
  },
  "nerw_pośrodkowy": {
    "latency_ms_max": 4.2,
    "conduction_velocity_m_s_min": 50
  }
}`;

type Patient = { id: number; first_name: string; last_name: string };

type NerveRow = {
  id: string;
  nerve_key: string;
  latency_ms: string;
  amplitude_mv: string;
  f_wave_latency_ms: string;
  conduction_velocity_m_s: string;
};

function emptyRow(nerve: string): NerveRow {
  return {
    id: crypto.randomUUID(),
    nerve_key: nerve,
    latency_ms: "",
    amplitude_mv: "",
    f_wave_latency_ms: "",
    conduction_velocity_m_s: "",
  };
}

function parseOptionalFloat(s: string): number | undefined {
  const t = s.trim();
  if (!t) return undefined;
  const n = Number(t.replace(",", "."));
  if (Number.isFinite(n)) return n;
  return undefined;
}

export default function Home() {
  const [token, setToken] = useState<string | null>(null);

  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [registerName, setRegisterName] = useState("");
  const [registerEmail, setRegisterEmail] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");
  const [authMode, setAuthMode] = useState<"login" | "register">("login");

  const [patients, setPatients] = useState<Patient[]>([]);
  const [patientId, setPatientId] = useState<string>("");
  const [newFirst, setNewFirst] = useState("");
  const [newLast, setNewLast] = useState("");
  const [newPesel, setNewPesel] = useState("");

  const [normsJson, setNormsJson] = useState(DEFAULT_NORMS);
  const [rows, setRows] = useState<NerveRow[]>(() => [
    emptyRow("nerw_pośrodkowy"),
    emptyRow("nerw_łokciowy"),
  ]);

  const [draft, setDraft] = useState("");
  const [deviations, setDeviations] = useState<DeviationFlag[]>([]);
  const [lastRaw, setLastRaw] = useState<Record<string, unknown> | null>(null);

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setToken(getStoredToken());
  }, []);

  const loadPatients = useCallback(async () => {
    const list = await apiFetch<Patient[]>("/patients");
    setPatients(list);
    setPatientId((prev) => {
      if (prev) return prev;
      return list.length ? String(list[0].id) : "";
    });
  }, []);

  useEffect(() => {
    if (!token) return;
    loadPatients().catch((e: unknown) =>
      setError(e instanceof Error ? e.message : "Błąd listy pacjentów"),
    );
  }, [token, loadPatients]);

  const normsObject = useMemo(() => {
    try {
      return JSON.parse(normsJson) as Record<string, unknown>;
    } catch {
      return {};
    }
  }, [normsJson]);

  const login = async () => {
    setError(null);
    setBusy(true);
    try {
      const res = await apiFetch<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email: loginEmail, password: loginPassword }),
        skipAuth: true,
      });
      setStoredToken(res.access_token);
      setToken(res.access_token);
      setPatientId("");
      await loadPatients();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Logowanie nie powiodło się");
    } finally {
      setBusy(false);
    }
  };

  const register = async () => {
    setError(null);
    setBusy(true);
    try {
      await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email: registerEmail,
          password: registerPassword,
          full_name: registerName,
        }),
        skipAuth: true,
      });
      setLoginEmail(registerEmail);
      setLoginPassword(registerPassword);
      setAuthMode("login");
      alert("Konto utworzone — możesz się zalogować.");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Rejestracja nie powiodła się");
    } finally {
      setBusy(false);
    }
  };

  const logout = () => {
    setStoredToken(null);
    setToken(null);
    setPatients([]);
    setPatientId("");
  };

  const createPatient = async () => {
    setError(null);
    setBusy(true);
    try {
      const body: Record<string, unknown> = {
        first_name: newFirst.trim(),
        last_name: newLast.trim(),
      };
      if (newPesel.trim()) body.pesel = newPesel.trim();
      const p = await apiFetch<Patient>("/patients", {
        method: "POST",
        body: JSON.stringify(body),
      });
      setPatients((prev) => [p, ...prev]);
      setPatientId(String(p.id));
      setNewFirst("");
      setNewLast("");
      setNewPesel("");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Nie udało się dodać pacjenta");
    } finally {
      setBusy(false);
    }
  };

  const updateRow = (id: string, patch: Partial<NerveRow>) => {
    setRows((prev) => prev.map((r) => (r.id === id ? { ...r, ...patch } : r)));
  };

  const analyze = async () => {
    setError(null);
    setBusy(true);
    try {
      const nerves = rows.map((r) => ({
        nerve_key: r.nerve_key,
        latency_ms: parseOptionalFloat(r.latency_ms),
        amplitude_mv: parseOptionalFloat(r.amplitude_mv),
        f_wave_latency_ms: parseOptionalFloat(r.f_wave_latency_ms),
        conduction_velocity_m_s: parseOptionalFloat(r.conduction_velocity_m_s),
      }));

      const body: Record<string, unknown> = {
        norms: normsObject,
        nerves,
        muscles: {},
      };
      const pid = Number(patientId);
      if (patientId && Number.isFinite(pid)) body.patient_id = pid;

      const res = await apiFetch<{
        raw_data: Record<string, unknown>;
        deviations: DeviationFlag[];
        ai_description_draft: string;
      }>("/analyze-emg", { method: "POST", body: JSON.stringify(body) });

      setLastRaw(res.raw_data);
      setDeviations(res.deviations ?? []);
      setDraft(res.ai_description_draft ?? "");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Analiza nie powiodła się");
    } finally {
      setBusy(false);
    }
  };

  const saveExamination = async () => {
    if (!patientId) {
      setError("Wybierz pacjenta.");
      return;
    }
    if (!draft.trim()) {
      setError("Brak treści opisu do zapisu.");
      return;
    }
    setError(null);
    setBusy(true);
    try {
      const nerves = rows.map((r) => ({
        nerve_key: r.nerve_key,
        latency_ms: parseOptionalFloat(r.latency_ms),
        amplitude_mv: parseOptionalFloat(r.amplitude_mv),
        f_wave_latency_ms: parseOptionalFloat(r.f_wave_latency_ms),
        conduction_velocity_m_s: parseOptionalFloat(r.conduction_velocity_m_s),
      }));
      const raw_emg_data = lastRaw ?? {
        patient_id: Number(patientId),
        norms: normsObject,
        nerves,
        muscles: {},
      };
      await apiFetch("/examinations/", {
        method: "POST",
        body: JSON.stringify({
          patient_id: Number(patientId),
          raw_emg_data,
          norms_snapshot: normsObject,
          final_description: draft.trim(),
          status: "approved",
        }),
      });
      setError(null);
      alert("Zapisano badanie w bazie.");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Zapis nie powiódł się");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="font-heading text-xl font-semibold tracking-tight text-foreground md:text-2xl">
              MedApp EMG / ENG
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Analiza parametrów nerwowo-mięśniowych, szkic opisu AI i
              zatwierdzenie dokumentacji.
            </p>
          </div>
          <div className="text-xs text-muted-foreground">
            API: <span className="font-mono">{apiUrl}</span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8">
        {!token ? (
          <Card className="mx-auto max-w-md">
            <CardHeader>
              <CardTitle>
                {authMode === "login" ? "Logowanie lekarza" : "Rejestracja"}
              </CardTitle>
              <CardDescription>
                {authMode === "login"
                  ? "Zaloguj się tokenem JWT, aby korzystać z analizy i zapisu."
                  : "Wymaga ALLOW_REGISTRATION=true po stronie API."}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              {authMode === "register" ? (
                <>
                  <div className="grid gap-2">
                    <Label htmlFor="reg-name">Imię i nazwisko</Label>
                    <Input
                      id="reg-name"
                      value={registerName}
                      onChange={(e) => setRegisterName(e.target.value)}
                      autoComplete="name"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="reg-email">E-mail</Label>
                    <Input
                      id="reg-email"
                      type="email"
                      value={registerEmail}
                      onChange={(e) => setRegisterEmail(e.target.value)}
                      autoComplete="email"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="reg-pass">Hasło</Label>
                    <Input
                      id="reg-pass"
                      type="password"
                      value={registerPassword}
                      onChange={(e) => setRegisterPassword(e.target.value)}
                      autoComplete="new-password"
                    />
                  </div>
                </>
              ) : (
                <>
                  <div className="grid gap-2">
                    <Label htmlFor="email">E-mail</Label>
                    <Input
                      id="email"
                      type="email"
                      value={loginEmail}
                      onChange={(e) => setLoginEmail(e.target.value)}
                      autoComplete="username"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="password">Hasło</Label>
                    <Input
                      id="password"
                      type="password"
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      autoComplete="current-password"
                    />
                  </div>
                </>
              )}
              {error && (
                <p className="border-destructive/30 bg-destructive/10 rounded-lg border px-3 py-2 text-sm text-destructive">
                  {error}
                </p>
              )}
            </CardContent>
            <CardFooter className="flex flex-wrap gap-2">
              {authMode === "login" ? (
                <>
                  <Button
                    type="button"
                    disabled={busy}
                    onClick={() => void login()}
                  >
                    Zaloguj
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    disabled={busy}
                    onClick={() => setAuthMode("register")}
                  >
                    Rejestracja
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    type="button"
                    disabled={busy}
                    onClick={() => void register()}
                  >
                    Utwórz konto
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    disabled={busy}
                    onClick={() => setAuthMode("login")}
                  >
                    Wróć do logowania
                  </Button>
                </>
              )}
            </CardFooter>
          </Card>
        ) : (
          <div className="grid gap-8 lg:grid-cols-2 lg:items-start">
            <div className="flex flex-col gap-6">
              <Card>
                <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-4">
                  <div>
                    <CardTitle>Sesja</CardTitle>
                    <CardDescription>
                      Jesteś zalogowany jako lekarz.
                    </CardDescription>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={logout}
                  >
                    Wyloguj
                  </Button>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Pacjent</CardTitle>
                  <CardDescription>
                    Wybierz pacjenta lub dodaj nowego (dane identyfikujące nie
                    są wysyłane do AI).
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col gap-4">
                  <div className="grid gap-2">
                    <Label>Aktywny pacjent</Label>
                    <select
                      className="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm shadow-sm outline-none ring-offset-background focus-visible:ring-2 focus-visible:ring-ring"
                      value={patientId}
                      onChange={(e) => setPatientId(e.target.value)}
                    >
                      <option value="">— wybierz —</option>
                      {patients.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.id} — {p.first_name} {p.last_name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="grid gap-3 sm:grid-cols-3">
                    <div className="grid gap-2">
                      <Label htmlFor="np">Imię</Label>
                      <Input
                        id="np"
                        value={newFirst}
                        onChange={(e) => setNewFirst(e.target.value)}
                        placeholder="Jan"
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="nl">Nazwisko</Label>
                      <Input
                        id="nl"
                        value={newLast}
                        onChange={(e) => setNewLast(e.target.value)}
                        placeholder="Kowalski"
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="pesel">PESEL (opcj.)</Label>
                      <Input
                        id="pesel"
                        value={newPesel}
                        onChange={(e) => setNewPesel(e.target.value)}
                        placeholder="11 cyfr"
                      />
                    </div>
                  </div>
                  <Button
                    type="button"
                    variant="secondary"
                    disabled={busy || !newFirst.trim() || !newLast.trim()}
                    onClick={() => void createPatient()}
                  >
                    Dodaj pacjenta
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Normy referencyjne (JSON)</CardTitle>
                  <CardDescription>
                    Edytuj progi dla parametrów i wpisów specyficznych dla
                    nerwu.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <textarea
                    className="min-h-[140px] w-full rounded-lg border border-input bg-background px-3 py-2 font-mono text-xs leading-relaxed shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    value={normsJson}
                    onChange={(e) => setNormsJson(e.target.value)}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Dane badania EMG</CardTitle>
                  <CardDescription>
                    Latencja, amplituda CMAP, fala F, prędkość przewodzenia.
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col gap-4">
                  {rows.map((row) => (
                    <div
                      key={row.id}
                      className="rounded-xl border border-border p-4"
                    >
                      <div className="mb-3 grid gap-2">
                        <Label>Nerw</Label>
                        <select
                          className="flex h-10 w-full rounded-lg border border-input bg-background px-3 text-sm shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                          value={row.nerve_key}
                          onChange={(e) =>
                            updateRow(row.id, { nerve_key: e.target.value })
                          }
                        >
                          {NERVE_OPTIONS.map((o) => (
                            <option key={o.value} value={o.value}>
                              {o.label}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="grid gap-3 sm:grid-cols-2">
                        <div className="grid gap-2">
                          <Label>Latencja (ms)</Label>
                          <Input
                            inputMode="decimal"
                            value={row.latency_ms}
                            onChange={(e) =>
                              updateRow(row.id, { latency_ms: e.target.value })
                            }
                          />
                        </div>
                        <div className="grid gap-2">
                          <Label>Amplituda (mV)</Label>
                          <Input
                            inputMode="decimal"
                            value={row.amplitude_mv}
                            onChange={(e) =>
                              updateRow(row.id, {
                                amplitude_mv: e.target.value,
                              })
                            }
                          />
                        </div>
                        <div className="grid gap-2">
                          <Label>Latencja fali F (ms)</Label>
                          <Input
                            inputMode="decimal"
                            value={row.f_wave_latency_ms}
                            onChange={(e) =>
                              updateRow(row.id, {
                                f_wave_latency_ms: e.target.value,
                              })
                            }
                          />
                        </div>
                        <div className="grid gap-2">
                          <Label>Przewodzenie (m/s)</Label>
                          <Input
                            inputMode="decimal"
                            value={row.conduction_velocity_m_s}
                            onChange={(e) =>
                              updateRow(row.id, {
                                conduction_velocity_m_s: e.target.value,
                              })
                            }
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                  <div className="flex flex-wrap gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        setRows((r) => [...r, emptyRow("nerw_pośrodkowy")])
                      }
                    >
                      Dodaj nerw
                    </Button>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      disabled={rows.length <= 1}
                      onClick={() => setRows((r) => r.slice(0, -1))}
                    >
                      Usuń ostatni
                    </Button>
                  </div>
                </CardContent>
                <CardFooter className="flex flex-col items-stretch gap-3 sm:flex-row sm:flex-wrap">
                  <Button
                    type="button"
                    disabled={busy}
                    onClick={() => void analyze()}
                  >
                    Generuj analizę
                  </Button>
                  <Button
                    type="button"
                    variant="secondary"
                    disabled={busy}
                    onClick={() => void saveExamination()}
                  >
                    Zatwierdź i zapisz
                  </Button>
                </CardFooter>
              </Card>

              {error && token && (
                <p className="border-destructive/30 bg-destructive/10 rounded-lg border px-4 py-3 text-sm text-destructive">
                  {error}
                </p>
              )}
            </div>

            <div className="min-h-[520px] lg:sticky lg:top-8">
              <DescriptionEditor
                value={draft}
                onChange={setDraft}
                deviations={deviations}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
