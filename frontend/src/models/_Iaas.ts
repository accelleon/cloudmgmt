/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { IaasParam } from './IaasParam';
import type { IaasType } from './IaasType';

export type _Iaas = {
    name: string;
    type: IaasType;
    params: Array<IaasParam>;
    id: number;
};
