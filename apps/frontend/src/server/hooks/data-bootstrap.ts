export interface DataBootstrapResult {
  status: "stubbed";
  hook: "data_bootstrap";
}

export const runDataBootstrap = (): DataBootstrapResult => {
  return {
    status: "stubbed",
    hook: "data_bootstrap",
  };
};
