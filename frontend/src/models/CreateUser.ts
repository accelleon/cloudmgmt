/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type CreateUser = {
    username: string;
    first_name: string;
    last_name: string;
    is_admin?: boolean;
    twofa_enabled?: null;
    password: string;
};
