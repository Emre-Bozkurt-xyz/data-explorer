// src/hooks/useUrlState.ts
import { useCallback } from "react";
import { useSearchParams } from "react-router-dom";

type Primitive = string | number | boolean;
type UrlStateShape = Record<string, Primitive>;

export function useUrlState<T extends UrlStateShape>(defaults: T) {
  const [searchParams, setSearchParams] = useSearchParams();

  // Build current state from URL + defaults
  const state = {} as T;
  (Object.keys(defaults) as (keyof T)[]).forEach((key) => {
    const defaultValue = defaults[key];
    const raw = searchParams.get(String(key));

    if (raw === null) {
      state[key] = defaultValue;
      return;
    }

    if (typeof defaultValue === "number") {
      const n = Number(raw);
      state[key] = (Number.isNaN(n) ? defaultValue : (n as any));
    } else if (typeof defaultValue === "boolean") {
      state[key] = (raw === "true") as any;
    } else {
      state[key] = raw as any;
    }
  });

  const setState = useCallback(
    (patch: Partial<T>) => {
      const next = new URLSearchParams(searchParams);

      (Object.keys(patch) as (keyof T)[]).forEach((key) => {
        const value = patch[key];
        const name = String(key);

        if (value === undefined || value === null || value === "") {
          next.delete(name);
        } else {
          next.set(name, String(value));
        }
      });

      setSearchParams(next, { replace: true });
    },
    [searchParams, setSearchParams],
  );

  return [state, setState] as const;
}
