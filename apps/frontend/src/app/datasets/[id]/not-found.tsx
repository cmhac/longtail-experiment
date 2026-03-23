import Link from "next/link";
import React from "react";
import type { JSX } from "react";

const DatasetNotFoundPage = (): JSX.Element => {
  return (
    <main data-testid="dataset-not-found-page">
      <h1>Dataset not found</h1>
      <p>The dataset you requested does not exist.</p>
      <p>
        <Link href="/datasets">Back to all datasets</Link>
      </p>
    </main>
  );
};

export default DatasetNotFoundPage;
