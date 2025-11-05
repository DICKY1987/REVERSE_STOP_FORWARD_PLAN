import { app } from './api/app';
const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Order service listening on :${port}`));
