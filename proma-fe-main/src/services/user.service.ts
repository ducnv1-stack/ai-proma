// file: services/user.service.ts

import {webApiClient} from '../libs/utils/apiClient';
import { User, UpdateUserRequest } from '../libs/types';

class UserService {
  async getMyProfile(): Promise<User> {
    return webApiClient<User>('/users/me', {
      method: 'GET',
    });
  }

  async updateMyProfile(data: UpdateUserRequest): Promise<User> {
    return webApiClient<User>('/users/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }
}

export const userService = new UserService();