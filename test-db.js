const { Client } = require("pg");

const client = new Client({
  connectionString: "postgresql://postgres:jGNEMNdfkQiNnUlvVSlbxQamOkwTAchb@centerbeam.proxy.rlwy.net:25167/railway",
  ssl: { rejectUnauthorized: false }
});

async function run() {
  try {
    await client.connect();
    console.log("Connected to Railway PostgreSQL");

    const res = await client.query(`
      SELECT column_name 
      FROM information_schema.columns 
      WHERE table_name = 'sale';
    `);

    console.log("sale table columns:");
    console.table(res.rows);

  } catch (err) {
    console.error(err);
  } finally {
    await client.end();
  }
}

run();