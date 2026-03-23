export interface EnvBootstrapResult {
  status: "stubbed";
  hook: "env_bootstrap";
}

export const runEnvBootstrap = (): EnvBootstrapResult => {
  return {
    status: "stubbed",
    hook: "env_bootstrap",
  };
};
