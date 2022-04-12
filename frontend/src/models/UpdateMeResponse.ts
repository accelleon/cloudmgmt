/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type UpdateMeResponse = {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
    is_admin: boolean;
    twofa_enabled: boolean;
    twofa_uri?: string;
};
