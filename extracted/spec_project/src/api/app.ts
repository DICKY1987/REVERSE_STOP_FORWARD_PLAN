import express from 'express';
import http from 'http';
import { createOrder } from './handler';
export const app = express();
app.use(express.json());
app.post('/orders', createOrder);
let server: http.Server | undefined;
export async function start(port = 0) {
  return new Promise<void>((resolve) => { server = app.listen(port, resolve); });
}
export async function stop() { return new Promise<void>((resolve) => server?.close(() => resolve())); }
