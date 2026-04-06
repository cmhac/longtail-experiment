import React from "react";
import type { JSX } from "react";
import { NotificationsPageClient } from "../../components/notifications/NotificationsPageClient";
import {
  PageHeaderKicker,
  PageHeaderSubtitle,
  PageHeaderTitle,
  PageHeaderWrapper,
} from "../../components/discovery/PageHeader";
import { SitePageFrame } from "../../shell/site-page-frame";

const NotificationsPage = (): JSX.Element => {
  return (
    <SitePageFrame
      activeTab="home"
      mainClassName="grid content-start gap-4"
      mainTestId="notifications-page"
    >
      <PageHeaderWrapper testId="notifications-page-header">
        <div className="grid gap-[0.45rem]">
          <PageHeaderKicker>Notification Center</PageHeaderKicker>
          <PageHeaderTitle>Notifications</PageHeaderTitle>
          <PageHeaderSubtitle>
            Review trend reversal alerts, manage read state, and track followed datasets.
          </PageHeaderSubtitle>
        </div>
      </PageHeaderWrapper>
      <NotificationsPageClient />
    </SitePageFrame>
  );
};

export default NotificationsPage;
