export interface PublishExtensionResult {
  status: "stubbed";
  hook: "publish_extension";
}

export const runPublishExtension = (): PublishExtensionResult => {
  return {
    status: "stubbed",
    hook: "publish_extension",
  };
};
