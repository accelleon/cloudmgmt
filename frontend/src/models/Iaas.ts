/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { _Account } from './_Account';
import type { IaasParam } from './IaasParam';
import type { IaasType } from './IaasType';

export type Iaas = {
    name: string;
    type: IaasType;
    params: Array<IaasParam>;
    id: number;
    accounts: Array<_Account>;
};
