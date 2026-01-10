export interface Credential {
  accessToken: string;
  refreshToken: string;
  expiresAt: string;
  account: string;
  scopes: string[];
  clientId?: string;
  tenantId?: string;
}

export interface CredentialStore {
  [service: string]: {
    [profileName: string]: Credential;
  };
}

export interface GraphEmail {
  id: string;
  subject: string;
  from: {
    emailAddress: {
      name: string;
      address: string;
    };
  };
  receivedDateTime: string;
  bodyPreview: string;
  body?: {
    contentType: string;
    content: string;
  };
  isRead: boolean;
  hasAttachments: boolean;
}

export interface GraphCalendarEvent {
  id: string;
  subject: string;
  start: {
    dateTime: string;
    timeZone: string;
  };
  end: {
    dateTime: string;
    timeZone: string;
  };
  location?: {
    displayName: string;
  };
  organizer?: {
    emailAddress: {
      name: string;
      address: string;
    };
  };
  attendees?: Array<{
    emailAddress: {
      name: string;
      address: string;
    };
    status?: {
      response: string;
    };
  }>;
  bodyPreview?: string;
  isAllDay?: boolean;
}

export interface MailFolder {
  id: string;
  displayName: string;
  parentFolderId?: string;
  childFolderCount: number;
  unreadItemCount: number;
  totalItemCount: number;
}
