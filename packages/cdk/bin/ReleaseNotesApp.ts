import {
  createApp,
  getConfigFromEnvVar,
} from "@nhsdigital/eps-cdk-constructs"
import {ReleaseNotes} from "../stacks/releaseNotes.ts"

async function main() {
  const {app, props} = createApp({
    productName: "ReleaseNotes",
    appName: "ReleaseNotes",
    repoName: "electronic-prescription-service-release-notes",
    driftDetectionGroup: "releaseNotes"
  })

  const releaseNotesStack = new ReleaseNotes(app, "ReleaseNotes", {
    ...props,
    stackName: getConfigFromEnvVar("stackName"),
  })

}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
