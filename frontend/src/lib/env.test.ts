import { describe, it, expect } from 'vitest';
import { getApiUrl } from './env';

describe('getApiUrl', () => {
  it('returns env override when set', () => {
    const original = process.env.NEXT_PUBLIC_API_URL;
    process.env.NEXT_PUBLIC_API_URL = 'https://example.test';
    expect(getApiUrl()).toBe('https://example.test');
    if (original) {
      process.env.NEXT_PUBLIC_API_URL = original;
    } else {
      delete process.env.NEXT_PUBLIC_API_URL;
    }
  });

  it('falls back to localhost when unset', () => {
    const original = process.env.NEXT_PUBLIC_API_URL;
    delete process.env.NEXT_PUBLIC_API_URL;
    expect(getApiUrl()).toBe('http://localhost:8000');
    if (original) {
      process.env.NEXT_PUBLIC_API_URL = original;
    }
  });
});
