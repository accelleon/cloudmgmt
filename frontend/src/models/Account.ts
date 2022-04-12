/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { _Iaas } from './_Iaas';

export type Account = {
    id?: number;
    name: string;
    iaas_id: number;
    data: Record<string, string>;
    iaas: _Iaas;
};
