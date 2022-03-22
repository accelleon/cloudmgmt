
export interface User {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  is_admin: boolean;
  twofa_enabled: boolean;
}

export interface UpdateUser {
  username?: string;
  password?: string;
  first_name?: string;
  last_name?: string;
  is_admin?: boolean;
  twofa_enabled?: boolean;
  twofa_code?: string;
}

export interface UpdateUserResp extends User {
  twofa_uri?: string;
}