import express from 'express';

const app = express();
app.use(express.json());

app.post('/normalize', (req, res) => {
    const jobs = req.body.map((j: any) => ({
        title: (j.raw_title || '').trim(),
        company: (j.raw_company || '').trim(),
        description: (j.raw_description || '').trim().toLowerCase()
    }));
    res.json(jobs);
});

app.listen(8082, () => console.log('Normalizer on :8082'));
